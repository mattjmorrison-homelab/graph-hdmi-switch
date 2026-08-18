import os
import time
from enum import Enum

import serial

DEVICE = os.environ.get("HDMI_SWITCH_DEVICE", "/dev/ttyUSB0")
BAUD_RATE = 9600
_RESPONSE_SIZE = 8
_RESPONSE_DELAY_SECONDS = 0.5
_QUERY_COMMAND = b"\xAA\xBB\x03\x10\x00\xEE"


class SwitchCommunicationError(Exception):
    """Raised when the TESmart switch doesn't respond as expected over serial."""


class HdmiInputPort(Enum):
    GOOGLE_TV = 1
    APPLE_TV = 2
    PS3 = 3
    PS4 = 4
    SWITCH = 5


def _set_input_command(port: HdmiInputPort) -> bytes:
    return b"\xAA\xBB\x03\x01" + bytes([port.value]) + b"\xEE"


def _send_command(command: bytes) -> HdmiInputPort:
    try:
        connection = serial.Serial(DEVICE, BAUD_RATE, timeout=1)
        connection.write(command)
        time.sleep(_RESPONSE_DELAY_SECONDS)
        response = connection.read(size=_RESPONSE_SIZE)
    except serial.SerialException as exc:
        raise SwitchCommunicationError(
            f"failed to communicate with switch at {DEVICE}: {exc}"
        ) from exc

    if len(response) < _RESPONSE_SIZE:
        raise SwitchCommunicationError(
            f"expected {_RESPONSE_SIZE} bytes from switch, got {len(response)}"
        )
    try:
        return HdmiInputPort(response[4] + 1)
    except ValueError as exc:
        raise SwitchCommunicationError(
            f"switch reported unknown port: {response[4] + 1}"
        ) from exc


def get_current_input() -> HdmiInputPort:
    return _send_command(_QUERY_COMMAND)


def set_input(port: HdmiInputPort) -> HdmiInputPort:
    return _send_command(_set_input_command(port))
