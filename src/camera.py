"""
Camera module for AwakeGuard.

Handles video device initialization, frame acquisition, and resource cleanup using OpenCV.
"""

import cv2
import logging
from config.config import CAMERA_INDEX

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Camera:
    """Manages OpenCV VideoCapture operations."""

    def __init__(self, camera_index=CAMERA_INDEX):
        """
        Initialize the Camera instance.

        :param camera_index: Index of the camera device (default from config).
        """
        self.camera_index = camera_index
        self.cap = None

    def open(self):
        """
        Open the camera device for video capture.

        :return: True if camera opened successfully, False otherwise.
        """
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            logger.error(f"Unable to open camera with index {self.camera_index}")
            return False
        logger.info(f"Camera index {self.camera_index} initialized successfully.")
        return True

    def get_frame(self):
        """
        Read a single frame from the camera.

        :return: Tuple (ret, frame) where ret is a boolean indicating success.
        """
        if self.cap is None or not self.cap.isOpened():
            return False, None
        return self.cap.read()

    def release(self):
        """Release the camera hardware resource."""
        if self.cap is not None:
            if self.cap.isOpened():
                self.cap.release()
            logger.info("Camera released.")

    def is_opened(self):
        """Check if camera capture device is active."""
        return self.cap is not None and self.cap.isOpened()


# Functional API functions matching module documentation requirements
def initialize_camera(camera_index=CAMERA_INDEX):
    """
    Convenience function to create and open a Camera instance.

    :param camera_index: Index of the camera to initialize.
    :return: Camera object or None if initialization fails.
    """
    cam = Camera(camera_index=camera_index)
    if cam.open():
        return cam
    return None


def get_frame(camera_obj):
    """
    Convenience function to retrieve a frame from a Camera object or cv2.VideoCapture object.

    :param camera_obj: Camera object or cv2.VideoCapture object.
    :return: Tuple (ret, frame).
    """
    if hasattr(camera_obj, "get_frame"):
        return camera_obj.get_frame()
    elif isinstance(camera_obj, cv2.VideoCapture):
        return camera_obj.read()
    return False, None


def release_camera(camera_obj):
    """
    Convenience function to release a Camera or cv2.VideoCapture object.

    :param camera_obj: Camera object or cv2.VideoCapture object.
    """
    if hasattr(camera_obj, "release"):
        camera_obj.release()
    elif isinstance(camera_obj, cv2.VideoCapture) and camera_obj.isOpened():
        camera_obj.release()