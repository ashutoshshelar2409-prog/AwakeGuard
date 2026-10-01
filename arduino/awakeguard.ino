
--**/
#include <Arduino.h>

const int BUZZER_PIN = 8;
const int LED_PIN = 13;

String inputString = "";
bool stringComplete = false;

void setup() {
  // Initialize serial communication at 9600 baud
  Serial.begin(9600);
  
  // Set alert output pins
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  
  // Ensure alert hardware starts in OFF state
  digitalWrite(BUZZER_PIN, LOW);
  digitalWrite(LED_PIN, LOW);
  
  // Reserve memory for serial input buffer
  inputString.reserve(64);
}

void loop() {
  // Read incoming serial data
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    if (inChar == '\n' || inChar == '\r') {
      if (inputString.length() > 0) {
        stringComplete = true;
      }
    } else {
      inputString += inChar;
    }
  }

  // Process completed command string
  if (stringComplete) {
    inputString.trim();
    
    if (inputString == "DROWSY") {
      digitalWrite(BUZZER_PIN, HIGH);
      digitalWrite(LED_PIN, HIGH);
    } else if (inputString == "NORMAL") {
      digitalWrite(BUZZER_PIN, LOW);
      digitalWrite(LED_PIN, LOW);
    }
    
    // Clear command buffer
    inputString = "";
    stringComplete = false;
  }
}