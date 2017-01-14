import RPi.GPIO as GPIO
from time import gmtime, strftime

GPIO.setmode(GPIO.BCM)

# Buttons on PINs 9, 10 and 11
GPIO.setup(9, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Sensor on PIN 17
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def btn1_callback(channel):
    print("falling edge detected on 9")

def btn2_callback(channel):
    print("falling edge detected on 10")

def btn3_callback(channel):
    print("falling edge detected on 11")


print(strftime("%Y-%m-%d %H:%M:%S", gmtime()))

GPIO.add_event_detect(9, GPIO.FALLING, callback=btn1_callback, bouncetime=300)
GPIO.add_event_detect(10, GPIO.FALLING, callback=btn2_callback, bouncetime=300)
GPIO.add_event_detect(11, GPIO.FALLING, callback=btn3_callback, bouncetime=300)

try:
    GPIO.wait_for_edge(17, GPIO.RISING)
    print('Edge detected on channel 17')



except KeyboardInterrupt:
    print("Keyboard Interrupt")
finally:
    GPIO.cleanup()
    print("Cleaned up pins")
