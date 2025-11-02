// ----------------------------------------------------
// 🪑 BackBeacon - Seat Module (Arduino Nano 33 IoT)
// ----------------------------------------------------
#define FSR_PIN A0
#define MOTOR_PIN 9

int fsrReading = 0;
int threshold = 150;   // Adjust based on FSR output
bool sitting = false;

void setup() {
  Serial.begin(9600);
  pinMode(MOTOR_PIN, OUTPUT);
  digitalWrite(MOTOR_PIN, LOW);
  Serial.println("Seat Module Ready...");
}

void loop() {
  fsrReading = analogRead(FSR_PIN);
  sitting = (fsrReading > threshold);

  // Send sitting status to Raspberry Pi
  if (sitting)
    Serial.println("SEATED");
  else
    Serial.println("EMPTY");

  // Listen for slouch alert signal from Raspberry Pi
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command == "SLOUCH_ALERT") {
      digitalWrite(MOTOR_PIN, HIGH);
      delay(3000); // Vibrate for 3 seconds
      digitalWrite(MOTOR_PIN, LOW);
    }
  }

  delay(1000);
}
