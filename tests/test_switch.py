from unittest.mock import Mock, patch

import pytest
import serial

from homelab_hdmi_switch.switch import (
    HdmiInputPort,
    SwitchCommunicationError,
    get_current_input,
    set_input,
)


def _mock_connection(response: bytes) -> Mock:
    connection = Mock()
    connection.read.return_value = response
    return connection


@patch("homelab_hdmi_switch.switch.time.sleep")
@patch("homelab_hdmi_switch.switch.serial.Serial")
def test_get_current_input_returns_current_port(
    mock_serial: Mock, mock_sleep: Mock
) -> None:
    mock_serial.return_value = _mock_connection(b"\x00\x00\x00\x00\x03\x00\x00\x00")

    result = get_current_input()

    assert result == HdmiInputPort.PS4
    mock_serial.return_value.write.assert_called_once_with(b"\xaa\xbb\x03\x10\x00\xee")


@patch("homelab_hdmi_switch.switch.time.sleep")
@patch("homelab_hdmi_switch.switch.serial.Serial")
def test_set_input_sends_command_and_returns_new_port(
    mock_serial: Mock, mock_sleep: Mock
) -> None:
    mock_serial.return_value = _mock_connection(b"\x00\x00\x00\x00\x01\x00\x00\x00")

    result = set_input(HdmiInputPort.APPLE_TV)

    assert result == HdmiInputPort.APPLE_TV
    mock_serial.return_value.write.assert_called_once_with(b"\xaa\xbb\x03\x01\x02\xee")


@patch("homelab_hdmi_switch.switch.time.sleep")
@patch("homelab_hdmi_switch.switch.serial.Serial")
def test_get_current_input_raises_on_serial_exception(
    mock_serial: Mock, mock_sleep: Mock
) -> None:
    mock_serial.side_effect = serial.SerialException("device not found")

    with pytest.raises(SwitchCommunicationError, match="device not found"):
        get_current_input()


@patch("homelab_hdmi_switch.switch.time.sleep")
@patch("homelab_hdmi_switch.switch.serial.Serial")
def test_get_current_input_raises_on_short_response(
    mock_serial: Mock, mock_sleep: Mock
) -> None:
    mock_serial.return_value = _mock_connection(b"\x00\x00")

    with pytest.raises(SwitchCommunicationError, match="expected 8 bytes"):
        get_current_input()


@patch("homelab_hdmi_switch.switch.time.sleep")
@patch("homelab_hdmi_switch.switch.serial.Serial")
def test_get_current_input_raises_on_unknown_port(
    mock_serial: Mock, mock_sleep: Mock
) -> None:
    mock_serial.return_value = _mock_connection(b"\x00\x00\x00\x00\x09\x00\x00\x00")

    with pytest.raises(SwitchCommunicationError, match="unknown port"):
        get_current_input()
