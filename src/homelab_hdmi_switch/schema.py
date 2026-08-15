# Apollo Federation subgraph schema for hdmi-switch service.
# Uses strawberry.federation.Schema to enable the _service { sdl } introspection
# field that Apollo Gateway/Router needs for subgraph composition.
import strawberry


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello from hdmi-switch"


schema = strawberry.federation.Schema(query=Query)
