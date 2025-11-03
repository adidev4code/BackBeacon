// ----------------------------------------------------
// 🪑 BackBeacon - Seat Detection Module (Improved Stability & Communication)
// ----------------------------------------------------
// Function: Stably detects seat occupancy using FSR sensor averaging.
// - Continuously sends "SEATED" or "EMPTY" to Raspberry Pi every second.
// - Responds to "SLOUCH_ALERT" by activating buzzer & motor for 3 sec.
// - Automatically stops the alert if the user gets up.
// ----------------------------------------------------

#define FSR_PIN A0
#define MOTOR_PIN 9
// Using a different pin for the buzzer as Pin 8 doesn't support PWM on Nano if needed later.
#define BUZZER_PIN 7

// --- Stability & Timing Constants ---
const int FSR_THRESHOLD = 150;      // Threshold to determine if seated. Adjust this value based on your FSR's sensitivity.
const int NUM_READINGS = 10;        // Number of readings to average for a stable result.
const unsigned long DEBOUNCE_DELAY = 2000; // 2 seconds to confirm a state change (sitting or leaving).
const unsigned long ALERT_DURATION = 3000; // 3 seconds for the slouch alert vibration/buzz.
const unsigned long SEND_INTERVAL = 1000;  // Send status to Pi every 1 second.

// --- Global Variables ---
bool isSeated = false;              // The official, debounced state of the seat.
bool alertActive = false;
unsigned long lastStateChangeTime = 0;
unsigned long alertStartTime = 0;
unsigned long lastSendTime = 0;

void setup() {
  Serial.begin(9600);
  pinMode(MOTOR_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(MOTOR_PIN, LOW);
  digitalWrite(BUZZER_PIN, LOW);
  Serial.println("Seat Module Ready...");
}

void loop() {
  // 1. Get a smoothed, stable reading from the FSR by averaging.
  int stableFsrReading = getStableFsrReading();
  bool currentlyDetected = (stableFsrReading > FSR_THRESHOLD);

  // 2. Check if the stable state has changed (debouncing).
  // This logic confirms if a person has genuinely sat down or left.
  if (currentlyDetected != isSeated && millis() - lastStateChangeTime > DEBOUNCE_DELAY) {
    isSeated = currentlyDetected;
    lastStateChangeTime = millis();
    Serial.print("STATE CHANGE CONFIRMED: ");
    Serial.println(isSeated ? "SEATED" : "EMPTY");

    // If the person leaves while an alert is active, stop it immediately.
    if (!isSeated) {
      stopAlert();
    }
  }

  // 3. Send the current confirmed status to the Pi repeatedly. 📡
  // This ensures the Pi always knows the correct state, even if it misses a message.
  if (millis() - lastSendTime > SEND_INTERVAL) {
    lastSendTime = millis();
    if (isSeated) {
      Serial.println("SEATED");
    } else {
      Serial.println("EMPTY");
    }
  }

  // 4. Handle incoming commands from the Pi.
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    if (command == "SLOUCH_ALERT" && isSeated) {
      startAlert();
    }
  }

  // 5. Manage the alert duration.
  if (alertActive && (millis() - alertStartTime > ALERT_DURATION)) {
    stopAlert();
  }
}

// ----------------------------------------------------
// 🔔 Helper Functions
// ----------------------------------------------------

/**
 * @brief Reads the FSR sensor multiple times and returns the average.
 * This function smooths out noisy readings to get a stable value.
 * @return The averaged sensor reading.
 */
int getStableFsrReading() {
  long total = 0;
  for (int i = 0; i < NUM_READINGS; i++) {
    total += analogRead(FSR_PIN);
    delay(5); // Small delay between readings
  }
  return total / NUM_READINGS;
}

void startAlert() {
  if (!alertActive) { // Prevent re-starting the alert if it's already running
    alertActive = true;
    alertStartTime = millis();
    digitalWrite(MOTOR_PIN, HIGH);
    digitalWrite(BUZZER_PIN, HIGH);
    Serial.println("ALERT: Slouch feedback activated...");
  }
}

void stopAlert() {
  alertActive = false;
  digitalWrite(MOTOR_PIN, LOW);
  digitalWrite(BUZZER_PIN, LOW);
  Serial.println("ALERT: Feedback stopped.");
}
