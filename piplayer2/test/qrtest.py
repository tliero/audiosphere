import RPi.GPIO as GPIO
import time
import subprocess
import select  # see http://stackoverflow.com/a/10759061/3761783

QR_SCANNER_TIMEOUT = 3


# photo sensor on PIN 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN)

# LED on PIN 27
GPIO.setup(27, GPIO.OUT)
GPIO.output(27, GPIO.LOW)

try:
    print('Start QR scan test')
    
    while True:
        time.sleep(0.25)
        if (GPIO.input(17) == GPIO.LOW):
            #print('LOW')
            GPIO.output(27, GPIO.LOW)
        else:
            print('Sensor active')
            GPIO.output(27, GPIO.HIGH)
            zbarcam = subprocess.Popen(['zbarcam', '--quiet', '--nodisplay', '--raw', '-Sdisable', '-Sqrcode.enable', '--prescale=320x240', '/dev/video0'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            poll_obj = select.poll()
            poll_obj.register(zbarcam.stdout, select.POLLIN)
            
            # wait for scan result (or timeout)
            start_time = time.time()
            poll_result = False
            while ((time.time() - start_time) < QR_SCANNER_TIMEOUT and (not poll_result)):
                poll_result = poll_obj.poll(100)
                
            if (poll_result):
                qr_code = zbarcam.stdout.readline().rstrip()
                qr_code = qr_code.decode("utf-8") # python3
                print("QR Code: {}".format(qr_code))
            else:
                print('Timeout on zbarcam')
            
            zbarcam.terminate()
            GPIO.output(27, GPIO.LOW)


except KeyboardInterrupt:
    print('bye')
    GPIO.cleanup()
