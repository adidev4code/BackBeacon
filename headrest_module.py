# ----------------------------------------------------
# BackBeacon - Headrest Module (FIXED NON-BLOCKING VERSION)
# ----------------------------------------------------
import RPi.GPIO as GPIO
import serial
import time
import firebase_admin
from firebase_admin import credentials, db

# --- GPIO Setup ---
GPIO.setwarnings(False) # Hides warnings about channels already in use
GPIO.setmode(GPIO.BCM)
TRIG = 23
ECHO = 24
BUZZER1 = 17
BUZZER2 = 27

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(BUZZER1, GPIO.OUT)
GPIO.setup(BUZZER2, GPIO.OUT)
GPIO.output(BUZZER1, False)
GPIO.output(BUZZER2, False)

# --- Firebase Setup ---
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://backbeacon-default-rtdb.asia-southeast1.firebasedatabase.app/'
})
ref = db.reference("/backbeacon")

# --- Serial Setup (to Arduino) ---
# Ensure the port name '/dev/ttyACM0' is correct for your setup
try:
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    time.sleep(2) # Give time for serial connection to establish
    print("Headrest Module Started...")
except serial.SerialException as e:
    print(f"Error: Could not open serial port. {e}")
    print("Please check connection and port name (e.g., /dev/ttyACM0 or /dev/ttyUSB0).")
    exit()


# --- Constants & State Variables ---
SLOUCH_THRESHOLD = 5.0  # cm beyond ideal distance
PI_ALERT_DURATION = 3.0 # seconds for the Pi buzzers

ideal_distance = None
current_status = "EMPTY"  # Track last known state
posture = "Empty"

# NEW: State variables to manage non-blocking alerts
pi_alert_active = False
pi_alert_start_time = 0

# --- Measure Distance Function ---
def measure_distance():
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)
    start_time = time.time()
    stop_time = time.time()
    # Save the start time of the echo pulse
    while GPIO.input(ECHO) == 0:
        start_time = time.time()
    # Save the arrival time of the echo pulse
    while GPIO.input(ECHO) == 1:
        stop_time = time.time()
    time_elapsed = stop_time - start_time
    # Speed of sound = 34300 cm/s. Divide by 2 for there-and-back journey.
    distance = (time_elapsed * 34300) / 2
    return round(distance, 2)

# --- Buzzer Control Functions (NEW) ---
def start_pi_buzzers():
    global pi_alert_active, pi_alert_start_time
    if not pi_alert_active:
        print("Slouch Detected -> Activating Pi Buzzers!")
        pi_alert_active = True
        pi_alert_start_time = time.time()
        GPIO.output(BUZZER1, True)
        GPIO.output(BUZZER2, True)

def stop_pi_buzzers():
    global pi_alert_active
    if pi_alert_active:
        print("Stopping Pi Buzzers.")
        pi_alert_active = False
        GPIO.output(BUZZER1, False)
        GPIO.output(BUZZER2, False)

# --- Main Loop ---
try:
    while True:
        # First, manage any ongoing alerts
        if pi_alert_active and (time.time() - pi_alert_start_time > PI_ALERT_DURATION):
            stop_pi_buzzers()

        # Second, check for new data from Arduino
        if ser.in_waiting > 0:
            seat_status = ser.readline().decode('utf-8', errors='ignore').strip()

            # Ignore empty or junk reads
            if seat_status not in ["SEATED", "EMPTY"]:
                continue

            # A. If the user is SEATED
            if seat_status == "SEATED":
                dist = measure_distance()

                if ideal_distance is None:
                    ideal_distance = dist
                    print(f"Ideal posture set at {dist} cm")

                diff = dist - ideal_distance
                
                if diff > SLOUCH_THRESHOLD:
                    posture = "Bad"
                    start_pi_buzzers() # Start the non-blocking alert
                    ser.write(b"SLOUCH_ALERT\n") # Tell Arduino to vibrate
                else:
                    posture = "Good"
                    # If posture becomes good, we can stop the alert early (optional)
                    # stop_pi_buzzers()
            
            # B. If the seat is EMPTY
            elif seat_status == "EMPTY":
                # THIS IS THE KEY FIX: If we get an EMPTY signal, immediately stop the buzzers.
                stop_pi_buzzers()
                posture = "Empty"
                ideal_distance = None # Reset ideal distance for the next user

            # Only upload to Firebase if the state has changed to avoid spamming
            if seat_status != current_status:
                current_status = seat_status
                print(f"Seat state changed: {current_status} | Posture: {posture}")
                data = {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "seat_status": current_status,
                    "posture": posture,
                    "ideal_distance": round(ideal_distance if ideal_distance else 0, 2)
                }
                ref.push(data)
                print("Data sent to Firebase:", data)

        time.sleep(0.1) # A small delay to keep the loop from running too fast

except KeyboardInterrupt:
    print("Stopping program...")

finally:
    GPIO.cleanup()
    ser.close()
    print("Clean exit complete.")
