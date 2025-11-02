# ----------------------------------------------------
# 🧍‍♂️ BackBeacon - Headrest Module (Raspberry Pi)
# ----------------------------------------------------
import RPi.GPIO as GPIO
import serial, time, json
import firebase_admin
from firebase_admin import credentials, db

# --- GPIO Setup ---
GPIO.setmode(GPIO.BCM)

TRIG = 23
ECHO = 24
BUZZER1 = 17
BUZZER2 = 27

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(BUZZER1, GPIO.OUT)
GPIO.setup(BUZZER2, GPIO.OUT)

# --- Firebase Setup ---
cred = credentials.Certificate("firebase-key.json")  # download your key from Firebase
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://backbeacon-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

ref = db.reference("/backbeacon")

# --- Serial Setup to Arduino ---
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
time.sleep(2)

print("Headrest Module Started...")

ideal_distance = None
slouch_threshold = 5.0  # cm beyond ideal distance to trigger alert

def measure_distance():
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    start, stop = time.time(), time.time()
    while GPIO.input(ECHO) == 0:
        start = time.time()
    while GPIO.input(ECHO) == 1:
        stop = time.time()
    elapsed = stop - start
    return round((elapsed * 34300) / 2, 2)

try:
    while True:
        if ser.in_waiting > 0:
            seat_status = ser.readline().decode().strip()

            if seat_status == "SEATED":
                dist = measure_distance()
                if ideal_distance is None:
                    ideal_distance = dist
                    print(f"Ideal posture set at {dist} cm")

                diff = dist - ideal_distance

                if diff > slouch_threshold:
                    print("⚠️ Slouch Detected")
                    ser.write(b"SLOUCH_ALERT\n")   # Vibrate on Arduino
                    GPIO.output(BUZZER1, True)
                    GPIO.output(BUZZER2, True)
                    time.sleep(5)
                    GPIO.output(BUZZER1, False)
                    GPIO.output(BUZZER2, False)

                    posture = "Bad"
                else:
                    posture = "Good"
            else:
                posture = "Empty"
                ideal_distance = None

            # --- Upload data to Firebase ---
            data = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "seat_status": seat_status,
                "posture": posture,
                "distance": ideal_distance if ideal_distance else 0
            }
            ref.push(data)

            print("Data sent to Firebase:", data)

        time.sleep(2)

except KeyboardInterrupt:
    print("Stopping program...")
finally:
    GPIO.cleanup()
    ser.close()
