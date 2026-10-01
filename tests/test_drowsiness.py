"""
Unit tests for AwakeGuard drowsiness detector logic.

Verifies that EAR thresholding and eye-closure duration timing discriminate correctly
between normal blinks and prolonged drowsiness.
"""

import pytest
from src.drowsiness_detector import DrowsinessDetector
from config.config import EAR_THRESHOLD, DROWSINESS_DURATION


def test_normal_ear_stays_normal():
    """Test that EAR values above threshold remain in NORMAL state."""
    detector = DrowsinessDetector(ear_threshold=0.25, drowsiness_duration=2.0)
    state, duration = detector.update(ear=0.30, current_time=100.0)
    assert state == "NORMAL"
    assert duration == 0.0
    assert not detector.is_drowsy(ear=0.30, current_time=100.0)


def test_short_low_ear_stays_normal():
    """Test that an EAR below threshold for less than the drowsiness duration remains NORMAL (blink)."""
    detector = DrowsinessDetector(ear_threshold=0.25, drowsiness_duration=2.0)
    
    # Eye closes at t = 100.0
    state, duration = detector.update(ear=0.18, current_time=100.0)
    assert state == "NORMAL"
    assert duration == 0.0

    # Eye still closed at t = 101.5 (1.5 seconds elapsed < 2.0s duration)
    state, duration = detector.update(ear=0.18, current_time=101.5)
    assert state == "NORMAL"
    assert duration == pytest.approx(1.5)


def test_prolonged_low_ear_becomes_drowsy():
    """Test that an EAR below threshold for >= drowsiness duration triggers DROWSY state."""
    detector = DrowsinessDetector(ear_threshold=0.25, drowsiness_duration=2.0)
    
    # Eye closes at t = 100.0
    detector.update(ear=0.15, current_time=100.0)
    
    # 1 second elapsed
    state, duration = detector.update(ear=0.15, current_time=101.0)
    assert state == "NORMAL"

    # 2.0 seconds elapsed -> Should transition to DROWSY
    state, duration = detector.update(ear=0.15, current_time=102.0)
    assert state == "DROWSY"
    assert duration == pytest.approx(2.0)

    # 2.5 seconds elapsed -> Remains DROWSY
    state, duration = detector.update(ear=0.15, current_time=102.5)
    assert state == "DROWSY"
    assert duration == pytest.approx(2.5)


def test_reopen_eyes_resets_to_normal():
    """Test that reopening eyes after being DROWSY immediately resets state to NORMAL."""
    detector = DrowsinessDetector(ear_threshold=0.25, drowsiness_duration=2.0)
    
    # Trigger DROWSY state
    detector.update(ear=0.15, current_time=100.0)
    detector.update(ear=0.15, current_time=102.5)
    assert detector.state == "DROWSY"

    # Eye reopens at t = 103.0
    state, duration = detector.update(ear=0.32, current_time=103.0)
    assert state == "NORMAL"
    assert duration == 0.0


def test_missing_face_resets_state_and_timer():
    """Test that face detection loss (ear=None) resets closure timer and maintains NORMAL state."""
    detector = DrowsinessDetector(ear_threshold=0.25, drowsiness_duration=2.0)
    
    # Start eye closure
    detector.update(ear=0.18, current_time=100.0)
    detector.update(ear=0.18, current_time=101.5)

    # Face lost at t = 101.8
    state, duration = detector.update(ear=None, current_time=101.8)
    assert state == "NORMAL"
    assert duration == 0.0
    assert detector.closure_start_time is None