# AwakeGuard V1
 
**Real-time driver drowsiness detection using computer vision and Arduino.**
 
AwakeGuard watches a driver's eyes through a webcam, measures how long they stay closed using the Eye Aspect Ratio (EAR), and triggers a buzzer and LED through an Arduino when prolonged closure indicates drowsiness.
 
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=flat-square&logo=opencv&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0097A7?style=flat-square)
![Arduino](https://img.shields.io/badge/Arduino-00979D?style=flat-square&logo=arduino&logoColor=white)
 
```text
Camera → Face Detection → Eye Landmarks → EAR → Drowsiness Logic → Serial → Arduino → Buzzer + LED
```
 
---
 
## Accomplishments
 
- **Accomplished** real-time driver eye monitoring **as measured by** every camera frame passing through the face, eye-landmark and EAR pipeline with live status shown on screen, **by doing** OpenCV video capture and MediaPipe facial landmark detection.
- **Accomplished** blink-versus-drowsiness discrimination **as measured by** a configurable EAR threshold (default `0.25`) combined with a closure-duration threshold (default `2.0 s`), **by doing** time-based Eye Aspect Ratio analysis so a normal blink never raises an alert.
- **Accomplished** automatic hardware alerting **as measured by** the Arduino receiving `DROWSY` and `NORMAL` commands, with the buzzer and LED turning on and off accordingly, **by doing** serial communication between Python and Arduino using PySerial.
- **Accomplished** a modular, testable design **as measured by** the drowsiness decision logic living in its own module with unit tests for normal EAR, short closure and prolonged closure, **by doing** separating camera, face detection, eye analysis, decision and hardware code into independent Python files.
- **Accomplished** live user feedback **as measured by** the OpenCV window displaying face status, left and right EAR, and the current state (`NORMAL` or `DROWSY`), **by doing** drawing a status overlay on each processed frame.
---
 
## How It Works
 
**1. Eye Aspect Ratio.** For each eye, six landmarks (P1 to P6) are taken from MediaPipe and EAR is computed. The value drops sharply when the eye closes.
 
$$
EAR = \frac{\lVert P2-P6 \rVert + \lVert P3-P5 \rVert}{2\,\lVert P1-P4 \rVert}
$$
 
The left and right values are averaged into one EAR per frame.
 
**2. Closure timing.** When EAR falls below `EAR_THRESHOLD`, a timer starts. If the eyes reopen before `DROWSINESS_DURATION` elapses, it counts as a blink. If they stay closed longer, the state becomes `DROWSY`.
 
```text
NORMAL ── EAR low ──► EYES CLOSED ── duration exceeded ──► DROWSY
   ▲                                                          │
   └──────────────────────── eyes reopen ─────────────────────┘
```
 
**3. Missing face.** If no face is found in a frame, the system reports `FACE NOT DETECTED` and does not classify the driver as drowsy on that basis alone.
 
**4. Alert.** Python sends a single serial command per state change. The Arduino only handles the physical alert.
 
| Command  | Arduino behavior           |
| -------- | -------------------------- |
| `NORMAL` | Buzzer off, LED off        |
| `DROWSY` | Buzzer on, LED on          |
 
---
 
## Getting Started
 
### Prerequisites
 
- Python 3.10+
- A webcam
- An Arduino board with a buzzer and LED connected (pin numbers are defined in `arduino/awakeguard.ino`)
- [Arduino IDE](https://www.arduino.cc/en/software) to upload the sketch
### Setup
 
```bash
git clone <your-repo-url>
cd AwakeGuard
pip install -r requirements.txt
```
 
1. Open `arduino/awakeguard.ino` in the Arduino IDE and upload it to your board.
2. Find the board's serial port (for example `COM3` on Windows) and set it in `config/config.py`.
3. Run the application:
```bash
python src/main.py
```
 
Press `q` in the video window to exit. The camera and serial port are released on exit.
 
### Configuration
 
All tunable values are in `config/config.py`.
 
| Parameter             | Purpose                              | Default |
| --------------------- | ------------------------------------ | ------: |
| `EAR_THRESHOLD`       | EAR below this means eyes closed     |  `0.25` |
| `DROWSINESS_DURATION` | Seconds of closure before `DROWSY`   |   `2.0` |
| `CAMERA_INDEX`        | Which camera to use                  |     `0` |
| `SERIAL_PORT`         | Arduino serial port                  |  `COM3` |
| `BAUD_RATE`           | Serial speed                         |  `9600` |
 
These are starting values. EAR varies with eye shape, camera angle and lighting, so calibrate them for your setup.
 
---
 
## Project Structure
 
```text
AwakeGuard/
├── src/
│   ├── main.py                 # Connects all modules
│   ├── camera.py               # Camera init, frame capture, release
│   ├── face_detector.py        # Face detection and landmark extraction
│   ├── eye_detector.py         # Eye landmarks and EAR calculation
│   ├── drowsiness_detector.py  # Threshold and timer logic
│   └── arduino.py              # Serial connection and commands
├── arduino/
│   └── awakeguard.ino          # Buzzer and LED control
├── config/
│   └── config.py               # Tunable parameters
├── tests/
│   └── test_drowsiness.py      # Unit tests for the decision logic
└── requirements.txt
```
 
## Testing
 
The drowsiness logic is tested independently of the camera and hardware.
 
```bash
pip install pytest
python -m pytest tests/
```
 
Covered cases: normal EAR stays `NORMAL`, a short low-EAR period stays `NORMAL`, and a prolonged low-EAR period becomes `DROWSY`.
 
---
 
## Limitations
 
AwakeGuard V1 is a prototype and does not guarantee driver safety. It is not a replacement for responsible driving or a certified vehicle safety system.
 
Accuracy can be reduced by:
 
- Poor or uneven lighting
- Camera position and angle
- Sunglasses or anything covering the eyes
- Landmark detection errors
- Individual differences in eye shape
V1 uses eye closure only. Yawning, head pose, GPS, emergency calling and vehicle control are out of scope.
 
## Roadmap
 
- [ ] Yawning detection
- [ ] Head-pose analysis
- [ ] Per-user EAR calibration
- [ ] Testing across more users and lighting conditions
---
 
**Author:** Ashutosh Shelar
 
```text
AwakeGuard/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── src/
│   ├── main.py
│   ├── camera.py
│   ├── face_detector.py
│   ├── eye_detector.py
│   ├── drowsiness_detector.py
│   └── arduino.py
│
├── arduino/
│   └── awakeguard.ino
│
├── config/
│   └── config.py
│
└── tests/
    └── test_drowsiness.py
```

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////
```text
                 START
                   │
                   ↓
            Initialize Camera
                   │
                   ↓
             Capture Frame
                   │
                   ↓
             Detect Face
                   │
          ┌────────┴────────┐
          │                 │
       Not Found          Found
          │                 │
          │                 ↓
          │          Detect Eye Landmarks
          │                 │
          │                 ↓
          │          Calculate EAR
          │                 │
          │                 ↓
          │          EAR < Threshold?
          │            /           \
          │          NO             YES
          │          │               │
          │          ↓               ↓
          │       NORMAL       Start/continue
          │                         timer
          │                           │
          │                           ↓
          │                    Duration > 2 sec?
          │                       /        \
          │                     NO          YES
          │                     │            │
          │                     ↓            ↓
          │                  NORMAL       DROWSY
          │                                  │
          │                                  ↓
          │                              Send Alert
          │                                  │
          └──────────────────────────────────┘
                           │
                           ↓
                     Next Frame
```