"""
Arduino Serial Communication module for AwakeGuard.

Handles serial connection to Arduino hardware, sending state transition commands
("DROWSY" or "NORMAL") to trigger buzzer and LED alerts.
"""

import time
import logging
import serial
from config.config import SERIAL_PORT, BAUD_RATE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ArduinoController:
    """Manages PySerial communication with Arduino board."""

    def __init__(self, port=SERIAL_PORT, baudrate=BAUD_RATE):
        """
        Initialize ArduinoController instance.

        :param port: Serial port string (e.g., "COM3" or "/dev/ttyUSB0").
        :param baudrate: Baud rate for serial communication (default 9600).
        """
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        self.last_sent_state = None
        self.connected = False

    def connect(self):
        """
        Attempt to establish serial connection with Arduino.

        :return: True if connected successfully, False otherwise.
        """
        try:
            self.serial = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2)  # Wait for Arduino serial interface reset
            self.connected = True
            logger.info(f"Connected to Arduino on port {self.port} at {self.baudrate} baud.")
            return True
        except serial.SerialException as e:
            logger.warning(
                f"Could not open serial port {self.port}: {e}. Running in standalone software mode."
            )
            self.connected = False
            self.serial = None
            return False

    def send_command(self, command):
        """
        Send a raw command string to the Arduino over serial.

        :param command: Command string ("NORMAL" or "DROWSY").
        """
        if not self.connected or self.serial is None:
            return

        try:
            cmd_bytes = (command.strip() + "\n").encode("utf-8")
            self.serial.write(cmd_bytes)
            self.serial.flush()
            logger.info(f"Serial command sent to Arduino: {command.strip()}")
        except serial.SerialException as e:
            logger.error(f"Error sending serial command: {e}")
            self.connected = False

    def update_state(self, new_state):
        """
        Update state and transmit command to Arduino ONLY when state changes.

        :param new_state: Current state string ("NORMAL" or "DROWSY").
        """
        if new_state != self.last_sent_state:
            self.send_command(new_state)
            self.last_sent_state = new_state

    def send_alert(self):
        """Helper to force send DROWSY alert command."""
        self.update_state("DROWSY")

    def stop_alert(self):
        """Helper to force send NORMAL alert stop command."""
        self.update_state("NORMAL")

    def close(self):
        """Ensure hardware alert is turned off and close serial connection."""
        if self.connected and self.serial is not None:
            try:
                self.send_command("NORMAL")
                time.sleep(0.1)
                self.serial.close()
                logger.info("Arduino serial port closed cleanly.")
            except Exception as e:
                logger.error(f"Error closing Arduino serial port: {e}")
            finally:
                self.connected = False
                self.serial = None


# Module-level convenience functions
def send_alert(controller=None):
    """Send alert via controller if provided."""
    if controller:
        controller.send_alert()


def stop_alert(controller=None):
    """Stop alert via controller if provided."""
    if controller:
        controller.stop_alert()