/* ------------------------------------------------------------
   BackBeacon Project - Seat Module (Arduino Nano 33 IoT)
   ------------------------------------------------------------
   - Detects seat occupancy using FSR-402 pressure sensor
   - Activates vibration motor for feedback when commanded
   - Sends seat status to Raspberry Pi via Serial (UART)
------------------------------------------------------------- */

const int fsrPin = A0;         // FSR pressure sensor pin
const int motorPin = 9;        // Vibration motor control pin
int fsrReading = 0;            // Pressure sensor value
bool seatOccupied = false;     // Seat occupancy flag
bool vibrationCommand = false; // Command from Pi

void setup() {
  Serial.begin(9600);          // Start serial communication
  pinMode(fsrPin, INPUT);
  pinMode(motorPin, OUTPUT);
  digitalWrite(motorPin, LOW);
}

void loop() {
  fsrReading = analogRead(fsrPin);

  // Check if someone is sitting
  if (fsrReading > 300) {
    seatOccupied = true;
  } else {
    seatOccupied = false;
  }

  // Send seat occupancy status to Raspberry Pi
  Serial.print("SEAT:");
  Serial.println(seatOccupied ? "1" : "0");

  // Check for commands from Raspberry Pi
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command == "VIB_ON") {
      digitalWrite(motorPin, HIGH);   // Start vibration
      vibrationCommand = true;
    } 
    else if (command == "VIB_OFF") {
      digitalWrite(motorPin, LOW);    // Stop vibration
      vibrationCommand = false;
    }
  }

  delay(500);  // Short delay for stable serial communication
}
