"""
AwakeGuard Configuration Module.

Centralized configuration settings for the AwakeGuard driver drowsiness detection system.
Modifying these values adjusts system sensitivity, camera selection, and Arduino communication parameters.
"""

# Eye Aspect Ratio (EAR) threshold. EAR below this value indicates closed eyes.
EAR_THRESHOLD = 0.25

# Duration in seconds of continuous eye closure required to trigger a DROWSY state.
DROWSINESS_DURATION = 2.0

# Camera index used by OpenCV VideoCapture (0 is typically the default built-in webcam).
CAMERA_INDEX = 0

# Serial communication port connected to the Arduino board (e.g., "COM3" on Windows, "/dev/ttyUSB0" on Linux).
SERIAL_PORT = "COM3"

# Serial baud rate for communicating with Arduino.
BAUD_RATE = 9600