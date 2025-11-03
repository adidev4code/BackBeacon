// ----------------------------------------------------
// 🪑 BackBeacon - Seat Module (Arduino Nano 33 IoT)
// ----------------------------------------------------
// Function: Detects if someone is sitting using FSR sensor
// Sends "SEATED" or "EMPTY" to Raspberry Pi via Serial
// Activates vibration motor when "SLOUCH_ALERT" command is received
// ----------------------------------------------------

#define FSR_PIN A0
#define MOTOR_PIN 9

int fsrReading = 0;
int threshold = 150;   // Adjust based on your FSR output
bool sitting = false;
bool motorActive = false;

void setup() {
  Serial.begin(9600);
  pinMode(MOTOR_PIN, OUTPUT);
  digitalWrite(MOTOR_PIN, LOW);
  Serial.println("Seat Module Ready...");
}

void loop() {
  fsrReading = analogRead(FSR_PIN);
  bool newSitting = (fsrReading > threshold);

  // Only send status when it changes (avoids spam)
  if (newSitting != sitting) {
    sitting = newSitting;
    if (sitting)
      Serial.println("SEATED");
    else
      Serial.println("EMPTY");
  }

  // Check for incoming command from Raspberry Pi
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command == "SLOUCH_ALERT" && sitting) {
      Serial.println("⚠️ Vibrating - Slouch Alert");
      digitalWrite(MOTOR_PIN, HIGH);
      motorActive = true;
      delay(3000); // Vibrate for 3 seconds
      digitalWrite(MOTOR_PIN, LOW);
      motorActive = false;
    }
  }

  delay(500);
}
