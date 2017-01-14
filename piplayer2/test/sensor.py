import RPi.GPIO as GPIO
import time

# photo sensor on PIN 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN)

# LED on PIN 27
GPIO.setup(27, GPIO.OUT)
GPIO.output(27, GPIO.LOW)

try:
    print('Start sensor test')
    
    while True:
        time.sleep(0.25)
        if (GPIO.input(17) == GPIO.LOW):
            print('LOW')
            GPIO.output(27, GPIO.LOW)
        else:
            print('HIGH')
            GPIO.output(27, GPIO.HIGH)

except KeyboardInterrupt:
    print('bye')
    GPIO.cleanup()

