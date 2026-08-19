import os
import time
from enum import Enum

import serial

DEVICE = os.environ.get("HDMI_SWITCH_DEVICE", "/dev/ttyUSB0")
BAUD_RATE = 9600
# The switch's documented response frame is 8 bytes, but real devices have
# been observed sending fewer (e.g. 6) — the only byte actually used is
# index 4, so that's the real minimum, not the full frame size. The
# original reference implementation never validated length at all.
_RESPONSE_SIZE = 8
_MIN_RESPONSE_SIZE = 5
_RESPONSE_DELAY_SECONDS = 0.5
_QUERY_COMMAND = b"\xaa\xbb\x03\x10\x00\xee"


class SwitchCommunicationError(Exception):
    """Raised when the TESmart switch doesn't respond as expected over serial."""


class HdmiInputPort(Enum):
    """The switch has 8 physical ports. Only 5 are currently wired to a
    device — the rest are reserved for future use and excluded from the
    `inputs` query, but still valid mutation targets if ever wired up.
    """

    APPLE_TV = 1
    PC = 2
    SWITCH = 3
    PS3 = 4
    PS4 = 5
    UNUSED_6 = 6
    UNUSED_7 = 7
    UNUSED_8 = 8


def _set_input_command(port: HdmiInputPort) -> bytes:
    return b"\xaa\xbb\x03\x01" + bytes([port.value]) + b"\xee"


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

    if len(response) < _MIN_RESPONSE_SIZE:
        raise SwitchCommunicationError(
            f"expected at least {_MIN_RESPONSE_SIZE} bytes from switch, "
            f"got {len(response)}"
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
