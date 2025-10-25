#Code:

import RPi.GPIO as GPIO
import time
import serial
import requests

# ------------------- GPIO Pins -------------------------
TRIG = 17
ECHO = 27
BUZZER = 22

# ------------------- Setup -----------------------------
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(BUZZER, GPIO.OUT)

# Serial to Arduino
arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
time.sleep(2) # Serial settle

# Dashboard endpoint
dashboard_url = "http://127.0.0.1:5000/update"

# ------------------- Functions -------------------------
def measure_distance():
    GPIO.output(TRIG, False)
    time.sleep(0.05)
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    start, stop = time.time(), time.time()

    while GPIO.input(ECHO) == 0:
        start = time.time()
    while GPIO.input(ECHO) == 1:
        stop = time.time()

    duration = stop - start
    distance = (duration * 34300) / 2
    return distance

def send_to_dashboard(posture):
    try:
        requests.post(dashboard_url, json={"posture": posture, "timestamp": time.time()})
    except:
        print("Dashboard not reachable")

# ------------------- Main Loop -------------------------
try:
    while True:
        distance = measure_distance()
        posture = "good"

        if distance > 25:  # Slouch threshold
            posture = "bad"
            GPIO.output(BUZZER, True)
            arduino.write(b'V')  # Tell Arduino to vibrate
        else:
            GPIO.output(BUZZER, False)
            arduino.write(b'N')  # Stop vibration

        # Update dashboard
        send_to_dashboard(posture)
        time.sleep(0.5)

except KeyboardInterrupt:
    GPIO.cleanup()
    arduino.close()
