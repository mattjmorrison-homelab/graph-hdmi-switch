# Apollo Federation subgraph schema for hdmi-switch service.
# Uses strawberry.federation.Schema to enable the _service { sdl } introspection
# field that Apollo Gateway/Router needs for subgraph composition.
import strawberry

from homelab_hdmi_switch import switch

HdmiInput = strawberry.enum(switch.HdmiInputPort, name="HdmiInput")


@strawberry.type
class Query:
    @strawberry.field
    def current_input(self) -> HdmiInput:
        return switch.get_current_input()


@strawberry.type
class Mutation:
    @strawberry.field
    def set_input(self, input: HdmiInput) -> HdmiInput:
        return switch.set_input(input)


schema = strawberry.federation.Schema(query=Query, mutation=Mutation)
