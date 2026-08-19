# Apollo Federation subgraph schema for hdmi-switch service.
# Uses strawberry.federation.Schema to enable the _service { sdl } introspection
# field that Apollo Gateway/Router needs for subgraph composition.
import strawberry

from homelab_hdmi_switch import switch
from homelab_hdmi_switch.input_config import CONFIGURED_INPUTS

HdmiInput = strawberry.enum(switch.HdmiInputPort, name="HdmiInput")


@strawberry.type
class Input:
    value: HdmiInput
    label: str
    icon: str
    hover_text: str
    is_active: bool


@strawberry.type
class Query:
    @strawberry.field
    def inputs(self) -> list[Input]:
        current = switch.get_current_input()
        return [
            Input(
                value=config.port,
                label=config.label,
                icon=config.icon,
                hover_text=config.hover_text,
                is_active=config.port == current,
            )
            for config in CONFIGURED_INPUTS
        ]


@strawberry.type
class Mutation:
    @strawberry.field
    def set_input(self, input: HdmiInput) -> HdmiInput:
        return switch.set_input(input)


schema = strawberry.federation.Schema(query=Query, mutation=Mutation)
