import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

GPIO.setup(27,GPIO.OUT)
GPIO.output(27,GPIO.HIGH)

