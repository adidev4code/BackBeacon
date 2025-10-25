"""
------------------------------------------------------------
BackBeacon Project - Headrest Module (Raspberry Pi)
------------------------------------------------------------
- Detects head position using HC-SR04 ultrasonic sensor
- Triggers buzzer when poor posture (slouch) detected
- Communicates with Arduino seat module via Serial (UART)
- Logs posture data to Firebase dashboard
------------------------------------------------------------
"""

import RPi.GPIO as GPIO
import time
import serial
import firebase_admin
from firebase_admin import credentials, db

# ----------------- Setup Section -----------------

# Ultrasonic pins
TRIG = 17
ECHO = 27
BUZZER = 22

# Distance thresholds (in cm)
NORMAL_DIST = 25
SLOUCH_DIST = 40

# Firebase setup
cred = credentials.Certificate("/home/pi/BackBeacon/firebase-credentials.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://your-project-id.firebaseio.com/'
})

# Serial communication setup with Arduino
ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)
ser.flush()

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(BUZZER, GPIO.OUT)

# ----------------- Function Definitions -----------------

def measure_distance():
    """Measure distance using HC-SR04 ultrasonic sensor"""
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    start_time = time.time()
    stop_time = time.time()

    while GPIO.input(ECHO) == 0:
        start_time = time.time()

    while GPIO.input(ECHO) == 1:
        stop_time = time.time()

    elapsed = stop_time - start_time
    distance = (elapsed * 34300) / 2  # in cm
    return distance

def update_firebase(status, distance):
    """Update posture status in Firebase"""
    ref = db.reference('BackBeacon')
    ref.update({
        'status': status,
        'distance_cm': distance,
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
    })

# ----------------- Main Loop -----------------
try:
    while True:
        # Check seat occupancy from Arduino
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            if "SEAT:1" in line:
                distance = measure_distance()

                if distance > SLOUCH_DIST:
                    GPIO.output(BUZZER, True)
                    ser.write(b"VIB_ON\n")  # Tell Arduino to vibrate
                    update_firebase("SLOUCH DETECTED", round(distance, 2))

                elif distance < NORMAL_DIST:
                    GPIO.output(BUZZER, False)
                    ser.write(b"VIB_OFF\n")
                    update_firebase("GOOD POSTURE", round(distance, 2))
            else:
                # No one seated
                GPIO.output(BUZZER, False)
                ser.write(b"VIB_OFF\n")
                update_firebase("IDLE", 0)

        time.sleep(0.5)

except KeyboardInterrupt:
    GPIO.cleanup()
    ser.close()
