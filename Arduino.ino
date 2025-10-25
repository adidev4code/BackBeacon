// Code:

// ------------------- Pin Definitions -------------------
const int fsrPin = A0;           // Pressure sensor
const int motorPin = 9;          // Vibration motor PWM
const int threshold = 200;       // Sitting threshold

// ------------------- Variables ------------------------
int fsrValue = 0;
char piCommand = 'N';            // Command received from Pi

// ------------------- Setup ----------------------------
void setup() {
  pinMode(fsrPin, INPUT);
  pinMode(motorPin, OUTPUT);
  Serial.begin(9600);            // Serial communication to Pi
}

// ------------------- Loop -----------------------------
void loop() {
  fsrValue = analogRead(fsrPin);

  // Send seat status to Pi
  if (fsrValue > threshold) {
    Serial.println("ACTIVE");    // User is sitting
  } else {
    Serial.println("INACTIVE");  // Seat empty
    digitalWrite(motorPin, LOW); // Turn off vibration
  }

  // Read command from Pi
  if (Serial.available() > 0) {
    piCommand = Serial.read();
    if (piCommand == 'V') {      
      analogWrite(motorPin, 200); // Activate motor
    } else {
      digitalWrite(motorPin, LOW);
    }
  }
  delay(100); // Stability delay
}
