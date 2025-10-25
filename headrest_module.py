"""
-------------------------------------------------------------
BackBeacon - Headrest Module (Raspberry Pi 4)
-------------------------------------------------------------
- Monitors head distance via HC-SR04 ultrasonic sensor
- Triggers buzzer when slouching
- Sends posture data to Firebase Realtime Database
-------------------------------------------------------------
"""

import RPi.GPIO as GPIO
import time
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db

# ------------------- GPIO Setup ------------------- #
TRIG = 17
ECHO = 27
BUZZER = 22

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(BUZZER, GPIO.OUT)

# ------------------- Firebase Setup ------------------- #
cred = credentials.Certificate('firebase-credentials.json')  # Add your JSON
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://YOUR_PROJECT.firebaseio.com/'
})
ref = db.reference('BackBeacon')

# ------------------- Constants ------------------- #
GOOD_THRESHOLD = 20    # cm
BUZZER_DURATION = 0.5  # seconds

# ------------------- Functions ------------------- #
def measure_distance():
    GPIO.output(TRIG, False)
    time.sleep(0.05)
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    pulse_start = time.time()
    pulse_end = time.time()

    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)
    return distance

def trigger_buzzer(duration):
    GPIO.output(BUZZER, GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(BUZZER, GPIO.LOW)

def update_firebase(status, distance):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ref.set({
        'status': status,
        'distance_cm': distance,
        'timestamp': timestamp
    })

# ------------------- Main Loop ------------------- #
try:
    while True:
        distance = measure_distance()

        if distance > GOOD_THRESHOLD:
            status = "GOOD POSTURE"
        else:
            status = "SLOUCH DETECTED"
            trigger_buzzer(BUZZER_DURATION)

        update_firebase(status, distance)
        print(f"{status} | Distance: {distance} cm")
        time.sleep(1)

except KeyboardInterrupt:
    GPIO.cleanup()
