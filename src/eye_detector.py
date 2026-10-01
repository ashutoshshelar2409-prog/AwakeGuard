"""
Eye Detector module for AwakeGuard.

Extracts eye landmark coordinates from MediaPipe face mesh landmarks and computes
the Eye Aspect Ratio (EAR) for left and right eyes.
"""

import math
import numpy as np

# Landmark indices for Left Eye (P1..P6)
# P1: Outer corner (33)
# P2: Upper vertical outer (160)
# P3: Upper vertical inner (158)
# P4: Inner corner (133)
# P5: Lower vertical inner (153)
# P6: Lower vertical outer (144)
LEFT_EYE_INDICES = [33, 160, 158, 133, 153, 144]

# Landmark indices for Right Eye (P1..P6)
# P1: Inner corner (362)
# P2: Upper vertical inner (385)
# P3: Upper vertical outer (387)
# P4: Outer corner (263)
# P5: Lower vertical outer (373)
# P6: Lower vertical inner (380)
RIGHT_EYE_INDICES = [362, 385, 387, 263, 373, 380]


def calculate_ear(eye_landmarks):
    """
    Calculate Eye Aspect Ratio (EAR) given 6 eye landmark points [P1, P2, P3, P4, P5, P6].

    EAR = ( ||P2 - P6|| + ||P3 - P5|| ) / ( 2 * ||P1 - P4|| )

    :param eye_landmarks: List or array of 6 (x, y) tuple coordinates.
    :return: Calculated EAR value as a float.
    """
    if len(eye_landmarks) < 6:
        return 0.0

    p1, p2, p3, p4, p5, p6 = eye_landmarks[:6]

    # Vertical distance 1: ||P2 - P6||
    v1 = math.dist(p2, p6)

    # Vertical distance 2: ||P3 - P5||
    v2 = math.dist(p3, p5)

    # Horizontal distance: ||P1 - P4||
    h = math.dist(p1, p4)

    if h == 0:
        return 0.0

    ear = (v1 + v2) / (2.0 * h)
    return ear


def get_eye_landmarks(landmarks, frame_width, frame_height):
    """
    Extract pixel coordinates for left and right eye landmarks from MediaPipe landmarks.

    :param landmarks: Landmark list returned by MediaPipe FaceMesh.
    :param frame_width: Pixel width of the camera frame.
    :param frame_height: Pixel height of the camera frame.
    :return: Tuple (left_eye_points, right_eye_points) where each is a list of (x, y) tuples.
    """
    if not landmarks:
        return [], []

    left_eye_pts = []
    for idx in LEFT_EYE_INDICES:
        lm = landmarks[idx]
        px = int(lm.x * frame_width)
        py = int(lm.y * frame_height)
        left_eye_pts.append((px, py))

    right_eye_pts = []
    for idx in RIGHT_EYE_INDICES:
        lm = landmarks[idx]
        px = int(lm.x * frame_width)
        py = int(lm.y * frame_height)
        right_eye_pts.append((px, py))

    return left_eye_pts, right_eye_pts


def process_eyes(landmarks, frame_width, frame_height):
    """
    Extract landmarks and compute left EAR, right EAR, and average EAR.

    :param landmarks: MediaPipe facial landmarks.
    :param frame_width: Width of image frame.
    :param frame_height: Height of image frame.
    :return: Tuple (left_ear, right_ear, avg_ear, left_eye_pts, right_eye_pts).
    """
    left_pts, right_pts = get_eye_landmarks(landmarks, frame_width, frame_height)
    if not left_pts or not right_pts:
        return 0.0, 0.0, 0.0, [], []

    left_ear = calculate_ear(left_pts)
    right_ear = calculate_ear(right_pts)
    avg_ear = (left_ear + right_ear) / 2.0

    return left_ear, right_ear, avg_ear, left_pts, right_pts