"""
Main Entry Point for AwakeGuard V1.

Connects Camera, Face Detection, Eye Landmark Extraction, Drowsiness Logic,
and Arduino Serial Alert System into a real-time computer vision pipeline.
"""

import sys
import time
import logging
import cv2

from config.config import (
    EAR_THRESHOLD,
    DROWSINESS_DURATION,
    CAMERA_INDEX,
    SERIAL_PORT,
    BAUD_RATE,
)
from src.camera import Camera
from src.face_detector import FaceDetector
from src.eye_detector import process_eyes
from src.drowsiness_detector import DrowsinessDetector
from src.arduino import ArduinoController

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("AwakeGuard")


def main():
    """Main execution loop for AwakeGuard."""
    logger.info("Initializing AwakeGuard V1 System...")

    # 1. Initialize Camera
    camera = Camera(camera_index=CAMERA_INDEX)
    if not camera.open():
        logger.critical(f"Could not access camera at index {CAMERA_INDEX}. Exiting.")
        sys.exit(1)

    # 2. Initialize Face Detector
    face_detector = FaceDetector(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    # 3. Initialize Drowsiness Detector
    drowsiness_detector = DrowsinessDetector(
        ear_threshold=EAR_THRESHOLD,
        drowsiness_duration=DROWSINESS_DURATION,
    )

    # 4. Initialize Arduino Controller
    arduino = ArduinoController(port=SERIAL_PORT, baudrate=BAUD_RATE)
    arduino.connect()

    logger.info("AwakeGuard started successfully. Press 'q' to quit.")

    try:
        while True:
            ret, frame = camera.get_frame()
            if not ret or frame is None:
                logger.warning("Failed to grab frame from camera.")
                time.sleep(0.01)
                continue

            height, width = frame.shape[:2]

            # Detect Face and Landmarks
            landmarks = face_detector.detect_face(frame)

            if landmarks:
                # Process eyes and compute EAR
                left_ear, right_ear, avg_ear, left_pts, right_pts = process_eyes(
                    landmarks, width, height
                )

                # Update Drowsiness State Machine
                state, duration = drowsiness_detector.update(avg_ear)

                # Draw eye landmarks/contours
                if left_pts:
                    for pt in left_pts:
                        cv2.circle(frame, pt, 2, (0, 255, 0), -1)
                if right_pts:
                    for pt in right_pts:
                        cv2.circle(frame, pt, 2, (0, 255, 0), -1)

                face_status = "FACE DETECTED"
                face_color = (0, 255, 0)
            else:
                # Face lost -> update state machine with None
                state, duration = drowsiness_detector.update(None)
                left_ear = right_ear = avg_ear = 0.0
                face_status = "FACE NOT DETECTED"
                face_color = (0, 165, 255)  # Orange

            # Transmit hardware alert command on state change
            arduino.update_state(state)

            # -------------------------------------------------------------
            # UI Status Overlay
            # -------------------------------------------------------------
            # Top Banner Box
            banner_color = (0, 0, 255) if state == "DROWSY" else (50, 50, 50)
            cv2.rectangle(frame, (0, 0), (width, 90), banner_color, -1)

            # System Header & State
            title_text = "AwakeGuard V1 - Driver Monitoring"
            cv2.putText(
                frame,
                title_text,
                (15, 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

            # State Indicator Text
            state_color = (0, 0, 255) if state == "DROWSY" else (0, 255, 0)
            state_text = f"STATE: {state}"
            cv2.putText(
                frame,
                state_text,
                (15, 65),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                state_color if state == "DROWSY" else (0, 255, 0),
                3 if state == "DROWSY" else 2,
                cv2.LINE_AA,
            )

            # Face Status & Telemetry (Left column)
            cv2.putText(
                frame,
                f"Face Status: {face_status}",
                (width - 260, 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                face_color,
                1,
                cv2.LINE_AA,
            )

            if landmarks:
                ear_info = f"Avg EAR: {avg_ear:.2f} (Thresh: {EAR_THRESHOLD})"
                cv2.putText(
                    frame,
                    ear_info,
                    (width - 260, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    1,
                    cv2.LINE_AA,
                )

                duration_info = f"Closure Time: {duration:.1f}s / {DROWSINESS_DURATION:.1f}s"
                timer_color = (0, 0, 255) if duration > 0 else (200, 200, 200)
                cv2.putText(
                    frame,
                    duration_info,
                    (width - 260, 75),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    timer_color,
                    1,
                    cv2.LINE_AA,
                )

            # Full Frame Alert Border when DROWSY
            if state == "DROWSY":
                cv2.rectangle(frame, (0, 0), (width - 1, height - 1), (0, 0, 255), 10)
                cv2.putText(
                    frame,
                    "!!! DROWSINESS ALERT DETECTED !!!",
                    (int(width / 2) - 220, height - 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 0, 255),
                    2,
                    cv2.LINE_AA,
                )

            # Show live frame
            cv2.imshow("AwakeGuard - Driver Drowsiness Detection", frame)

            # Check keypress 'q' or ESC to exit
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q") or key == 27:
                logger.info("User quit requested.")
                break

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received.")

    finally:
        # Resource Cleanup
        logger.info("Cleaning up resources...")
        arduino.close()
        face_detector.close()
        camera.release()
        cv2.destroyAllWindows()
        logger.info("AwakeGuard shutdown complete.")


if __name__ == "__main__":
    main()