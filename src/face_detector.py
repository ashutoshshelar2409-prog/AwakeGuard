"""
Face Detector module for AwakeGuard.

Uses MediaPipe FaceMesh to detect facial landmarks in video frames.
"""

import cv2
import mediapipe as mp


class FaceDetector:
    """Detects facial landmarks using MediaPipe Face Mesh solution."""

    def __init__(
        self,
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ):
        """
        Initialize the MediaPipe Face Mesh model.

        :param static_image_mode: Whether to treat input as static images or video stream.
        :param max_num_faces: Maximum number of faces to detect.
        :param refine_landmarks: Whether to refine landmarks around eyes and lips.
        :param min_detection_confidence: Minimum confidence threshold for face detection.
        :param min_tracking_confidence: Minimum confidence threshold for landmark tracking.
        """
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=static_image_mode,
            max_num_faces=max_num_faces,
            refine_landmarks=refine_landmarks,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

    def detect_face(self, frame):
        """
        Process a video frame and extract facial landmarks for the primary face.

        :param frame: BGR image frame from OpenCV.
        :return: Normalized landmark list for the first detected face, or None if no face is found.
        """
        if frame is None:
            return None

        # Convert image from BGR to RGB as required by MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            return results.multi_face_landmarks[0].landmark
        return None

    def close(self):
        """Release MediaPipe resources."""
        self.face_mesh.close()


# Functional API wrapper
def detect_face(frame, detector=None):
    """
    Convenience function for face detection.

    :param frame: Input BGR frame.
    :param detector: Optional FaceDetector instance. If None, a temporary detector is created.
    :return: Landmark list or None.
    """
    if detector is None:
        detector = FaceDetector()
        landmarks = detector.detect_face(frame)
        detector.close()
        return landmarks
    return detector.detect_face(frame)