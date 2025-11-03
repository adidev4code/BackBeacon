// ----------------------------------------------------
// 🪑 BackBeacon - Seat Detection Module (Final Stable Version)
// ----------------------------------------------------
// Purpose: Detect seat occupancy using FSR sensor and activate buzzer accordingly
// Hardware: Arduino + FSR Sensor + Buzzer + Vibration Motor (optional)
// ----------------------------------------------------

#define FSR_PIN A0        // Analog pin for FSR sensor
#define BUZZER_PIN 8      // Digital pin for buzzer
#define MOTOR_PIN 9       // Optional vibration motor pin (can remove if unused)

int fsrReading = 0;       
int threshold = 150;      // Base FSR threshold (adjust after calibration)
bool isSeated = false;    
unsigned long lastChangeTime = 0;
unsigned long debounceDelay = 2000;  // 2 sec debounce to confirm stable reading

void setup() {
  Serial.begin(9600);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(MOTOR_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);
  digitalWrite(MOTOR_PIN, LOW);
  Serial.println("BackBeacon System Started - Waiting for Seat Input...");
}

void loop() {
  fsrReading = analogRead(FSR_PIN);
  Serial.print("FSR Reading: ");
  Serial.println(fsrReading);

  // If FSR value crosses the threshold (someone sits)
  if (fsrReading > threshold && !isSeated) {
    // Only change state if stable for debounce period
    if (millis() - lastChangeTime > debounceDelay) {
      isSeated = true;
      Serial.println("✅ Seat Occupied!");
      digitalWrite(BUZZER_PIN, HIGH);  // Activate buzzer briefly for feedback
      digitalWrite(MOTOR_PIN, HIGH);
      delay(500);
      digitalWrite(BUZZER_PIN, LOW);
      digitalWrite(MOTOR_PIN, LOW);
    }
    lastChangeTime = millis();
  }

  // If FSR value drops below threshold (person gets up)
  else if (fsrReading < threshold && isSeated) {
    // Only confirm if reading stays low for debounce period
    if (millis() - lastChangeTime > debounceDelay) {
      isSeated = false;
      Serial.println("🚶 Seat Vacated!");
      digitalWrite(BUZZER_PIN, LOW);
      digitalWrite(MOTOR_PIN, LOW);
    }
    lastChangeTime = millis();
  }

  delay(200); // Small delay for stability
}
