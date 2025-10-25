/* ------------------------------------------------------------
   BackBeacon - Seat Module (Arduino Nano 33 IoT)
-------------------------------------------------------------
   - Detects seat occupancy using FSR-402 pressure sensor
   - Triggers vibration motor for poor posture alerts
   - Sends occupancy data to Raspberry Pi via UART
------------------------------------------------------------ */

const int fsrPin = A0;       // FSR analog input
const int vibPin = 9;        // Vibration motor PWM output
const int threshold = 300;   // Pressure threshold to detect user presence

int fsrValue = 0;

void setup() {
  Serial.begin(9600);        // UART communication
  pinMode(vibPin, OUTPUT);
}

void loop() {
  fsrValue = analogRead(fsrPin); // Read pressure sensor

  if (fsrValue > threshold) {
    // User is sitting
    analogWrite(vibPin, 0);  // No vibration initially
    Serial.println("SEATED");
  } else {
    // User not seated
    analogWrite(vibPin, 0);  // Ensure motor off
    Serial.println("IDLE");
  }

  delay(200);
}

// Function to trigger vibration for poor posture
void triggerVibration(int intensity, int duration_ms) {
  analogWrite(vibPin, intensity);
  delay(duration_ms);
  analogWrite(vibPin, 0);
}
