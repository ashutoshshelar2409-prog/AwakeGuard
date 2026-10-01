"""
Drowsiness Detector module for AwakeGuard.

Main decision-making algorithm that evaluates Eye Aspect Ratio (EAR) values
against a configurable threshold over time to detect prolonged eye closure (drowsiness).
"""

import time
from config.config import EAR_THRESHOLD, DROWSINESS_DURATION


class DrowsinessDetector:
    """Evaluates EAR stream and tracks closure duration to determine drowsiness status."""

    def __init__(self, ear_threshold=EAR_THRESHOLD, drowsiness_duration=DROWSINESS_DURATION):
        """
        Initialize DrowsinessDetector.

        :param ear_threshold: EAR value below which eyes are classified as closed.
        :param drowsiness_duration: Seconds of continuous closure before declaring state as DROWSY.
        """
        self.ear_threshold = ear_threshold
        self.drowsiness_duration = drowsiness_duration
        self.closure_start_time = None
        self.state = "NORMAL"

    def update(self, ear, current_time=None):
        """
        Update detector state with the latest EAR reading.

        :param ear: Current average EAR (float), or None if no face detected.
        :param current_time: Explicit timestamp (float, seconds). If None, time.time() is used.
        :return: Tuple (state, duration) where state is "NORMAL" or "DROWSY" and duration is closure time in seconds.
        """
        if current_time is None:
            current_time = time.time()

        # If face is lost or EAR is unavailable, reset timer and keep status NORMAL
        if ear is None:
            self.closure_start_time = None
            self.state = "NORMAL"
            return self.state, 0.0

        if ear < self.ear_threshold:
            if self.closure_start_time is None:
                self.closure_start_time = current_time

            duration = current_time - self.closure_start_time

            if duration >= self.drowsiness_duration:
                self.state = "DROWSY"
            else:
                self.state = "NORMAL"
        else:
            self.closure_start_time = None
            duration = 0.0
            self.state = "NORMAL"

        return self.state, duration

    def is_drowsy(self, ear, current_time=None):
        """
        Convenience method returning True if current state is DROWSY.

        :param ear: Current average EAR.
        :param current_time: Optional explicit timestamp.
        :return: Boolean indicating if driver is drowsy.
        """
        state, _ = self.update(ear, current_time=current_time)
        return state == "DROWSY"

    def reset(self):
        """Reset closure timer and state to initial default state (NORMAL)."""
        self.closure_start_time = None
        self.state = "NORMAL"