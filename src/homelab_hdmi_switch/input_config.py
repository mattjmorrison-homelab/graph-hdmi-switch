from dataclasses import dataclass

from homelab_hdmi_switch.switch import HdmiInputPort


@dataclass(frozen=True)
class InputConfig:
    port: HdmiInputPort
    label: str
    icon: str
    hover_text: str


# Display order matches the requested UI layout: the first entry renders as
# a full-width "hero" row, the rest pair up two-per-row. Ports not listed
# here are physically unused and excluded from the `inputs` query, but
# remain valid `setInput` targets if ever wired up.
CONFIGURED_INPUTS: tuple[InputConfig, ...] = (
    InputConfig(HdmiInputPort.APPLE_TV, "Apple TV", "tv", "Apple TV"),
    InputConfig(HdmiInputPort.PC, "PC", "monitor", "PC"),
    InputConfig(HdmiInputPort.SWITCH, "Switch", "joystick", "Nintendo Switch"),
    InputConfig(HdmiInputPort.PS3, "PS3", "gamepad", "PlayStation 3"),
    InputConfig(HdmiInputPort.PS4, "PS4", "gamepad-2", "PlayStation 4"),
)
