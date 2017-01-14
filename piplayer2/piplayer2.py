# piplayer2 - The AudioSphere
# http://www.tilman.de/piplayer2
import RPi.GPIO as GPIO
import logging
import time
import subprocess
import select  # for polling zbarcam, see http://stackoverflow.com/a/10759061/3761783
import os


# Configuration
MUSIC_BASE_DIRECTORY = "/home/pi/music/"
SOUND_SCANNING = "/home/pi/piplayer2/sounds/scanning.mp3"
SOUND_OK = "/home/pi/piplayer2/sounds/ok.mp3"
SOUND_SCAN_FAIL = "/home/pi/piplayer2/sounds/fail.mp3"
SOUND_PLAYBACK_ERROR = "/home/pi/piplayer2/sounds/error.mp3"
QR_SCANNER_TIMEOUT = 3


logging.basicConfig(level=logging.INFO, format='%(asctime)s.%(msecs)d %(levelname)s - %(message)s')
logging.info('Initializing')

GPIO.setmode(GPIO.BCM)

# photo sensor on PIN 17
GPIO.setup(17, GPIO.IN)

# IR LED on PIN 22
GPIO.setup(22, GPIO.OUT)
GPIO.output(22, GPIO.LOW)

# LED on PIN 27
GPIO.setup(27, GPIO.OUT)
GPIO.output(27, GPIO.LOW)

# Buttons on PINs 9, 10 and 11
GPIO.setup(9, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_UP)


position = 0

def btn1_callback(channel):
    logging.debug('PREV_CALLBACK')
    out, err = subprocess.Popen(['mocp','-Q', '%state'], stdout=subprocess.PIPE).communicate()
    if (out.decode("utf-8").startswith('PLAY')):
        out, err = subprocess.Popen(['mocp','-Q', '%cs'], stdout=subprocess.PIPE).communicate()
        position = int(out.decode("utf-8"))
        if (position < 4):
            logging.debug('mocp --previous')
            subprocess.call(["mocp", "--previous"])
        else:
            logging.debug('mocp --jump 0s')
            subprocess.call(["mocp", "--jump", "0s"])
       
def btn2_callback(channel):
    logging.debug('mocp --toggle-pause')
    subprocess.call(["mocp", "--toggle-pause"])

def btn3_callback(channel):
    logging.debug('mocp --next')
    subprocess.call(["mocp", "--next"])
    
    

GPIO.add_event_detect(9, GPIO.FALLING, callback=btn1_callback, bouncetime=1000)
GPIO.add_event_detect(10, GPIO.FALLING, callback=btn2_callback, bouncetime=400)
GPIO.add_event_detect(11, GPIO.FALLING, callback=btn3_callback, bouncetime=400)

try:
    logging.info('Start moc server')
    subprocess.call(["mocp", "--server"])
    subprocess.call(["mocp", "--clear"])
    subprocess.call(["mocp", "-l", SOUND_OK])
    
    while True:
        logging.debug('Wait for photo sensor')
        GPIO.wait_for_edge(17, GPIO.RISING)
        
        logging.debug('Photo sensor active, activating light and camera')
        subprocess.call(["mocp", "-l", SOUND_SCANNING])
        
        # turn LED on
        GPIO.output(27, GPIO.HIGH)
        
        # scan QR code
        zbarcam = subprocess.Popen(['zbarcam', '--quiet', '--nodisplay', '--raw', '-Sdisable', '-Sqrcode.enable', '--prescale=320x240', '/dev/video0'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        poll_obj = select.poll()
        poll_obj.register(zbarcam.stdout, select.POLLIN)
        
        # wait for scan result (or timeout)
        start_time = time.time()
        poll_result = False
        while ((time.time() - start_time) < QR_SCANNER_TIMEOUT and (not poll_result)):
            poll_result = poll_obj.poll(100)

        if (poll_result):
            
            try:
                qr_code = zbarcam.stdout.readline().rstrip()
                qr_code = qr_code.decode("utf-8") # python3
                logging.info("QR Code: {}".format(qr_code))
                
                if (not qr_code.startswith("http://")):
                    # create full path
                    full_path = MUSIC_BASE_DIRECTORY + qr_code
                    logging.debug("Full Path {}".format(full_path))
                    
                    if (not os.path.isfile(full_path)):
                        logging.debug("not a file, add as directory")
                        directory = full_path
                        logging.debug("Directory {}".format(directory))
                    else:
                        logging.debug("it's a file")
                        directory = os.path.dirname(os.path.realpath(full_path))
                        filename = os.path.basename(full_path)
                        logging.debug("Directory {}".format(directory))
                        logging.debug("Filename {}".format(filename))
                    
                    os.chdir(directory)
                    
                else:
                    logging.debug("URL, open as stream")
                    stream_url = qr_code

                subprocess.call(["mocp", "--clear"])
                subprocess.call(["mocp", "--stop"])

                logging.debug("Stopped")
                
                # play confirmation sound
                subprocess.call(["mocp", "-l", SOUND_OK])
                
                if ('stream_url' in locals()):
                    logging.debug("Add stream")
                    subprocess.check_call(["mocp", "-a", stream_url])
                    del stream_url
                elif ('filename' in locals()):
                    logging.debug("Add file {}".format(filename))
                    subprocess.check_call(["mocp", "-a", filename])
                    del filename
                else:
                    logging.debug("Add directory {}".format(directory))
                    subprocess.check_call(["mocp", "-a", "."])
                
                logging.debug("Start playback")
                subprocess.check_call(["mocp", "-p"])
                
            except subprocess.CalledProcessError as e:
                logging.error("Error starting playback, mocp returned {}".format(e.returncode))
                logging.error(e.output)
                subprocess.call(["mocp", "-l", SOUND_PLAYBACK_ERROR])
            except FileNotFoundError as e:
                logging.error("Could not open directory {}".format(directory))
                subprocess.call(["mocp", "-l", SOUND_PLAYBACK_ERROR])

        else:
            logging.warning('Timeout on zbarcam')
            subprocess.call(["mocp", "-l", SOUND_SCAN_FAIL])
            
        zbarcam.terminate()
        
        # LED off
        GPIO.output(27, GPIO.LOW)

        # wait until sensor is not blocked anymore
        if (GPIO.input(17) == GPIO.HIGH):
            GPIO.wait_for_edge(17, GPIO.FALLING)
            time.sleep(1)

        
# Exit when Ctrl-C is pressed
except KeyboardInterrupt:
    logging.info('Shutdown')
    
finally:
    logging.info('Close moc server')
    subprocess.call(["mocp", "--exit"])
    logging.info('Reset GPIO configuration and close')
    GPIO.cleanup()



