import uvicorn

from starlette.applications import Starlette

from a2a.server.request_handlers import (
    DefaultRequestHandler
)

from a2a.server.routes import (
    create_agent_card_routes,
    create_jsonrpc_routes
)

from a2a.server.tasks import (
    InMemoryTaskStore
)

from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentInterface,
    AgentSkill
)

from a2a.utils.constants import (
    AGENT_CARD_WELL_KNOWN_PATH
)

from agentic_ai.a2a.recommendation_executor import (RecommendationAgentExecutor)

HOST = "127.0.0.1"
PORT = 9000

BASE_URL = (
    f"http://{HOST}:{PORT}"
)

# ============================================================
# AGENT CARD
# ============================================================

agent_card = AgentCard(

    name="Recommendation Agent",

    description=(
        "Combines information received from "
        "multiple specialized agents and "
        "generates recommendations."
    ),

    version="1.0.0",

    default_input_modes=[
        "text/plain"
    ],

    default_output_modes=[
        "text/plain"
    ],

    capabilities=AgentCapabilities(
        streaming=False
    ),

    supported_interfaces=[
        AgentInterface(
            protocol_binding="JSONRPC",

            url=BASE_URL,

            protocol_version="1.0"
        )
    ],

    skills=[
        AgentSkill(

            id="recommendation",

            name="Generate Recommendation",

            description=(
                "Combines user, weather and "
                "finance information."
            ),

            input_modes=[
                "text/plain"
            ],

            output_modes=[
                "text/plain"
            ],

            tags=[
                "recommendation",
                "multi-agent",
                "a2a"
            ],

            examples=[
                "Recommend what I should do today",
                "Give me a personalized recommendation"
            ]
        )
    ]
)

# ============================================================
# EXECUTOR
# ============================================================

executor = RecommendationAgentExecutor()

# ============================================================
# REQUEST HANDLER
# ============================================================

handler = DefaultRequestHandler(

    agent_executor=executor,

    task_store=InMemoryTaskStore(),

    agent_card=agent_card
)

# ============================================================
# ROUTES
# ============================================================

routes = []

routes.extend(
    create_agent_card_routes(
        agent_card,
        card_url=(
            AGENT_CARD_WELL_KNOWN_PATH
        )
    )
)

routes.extend(
    create_jsonrpc_routes(
        handler,
        rpc_url="/"
    )
)

# ============================================================
# STARLETTE APP
# ============================================================

app = Starlette(
    routes=routes
)

# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":
    print("\n========================================")
    print("RECOMMENDATION A2A SERVER")
    print("========================================")

    print(
        "Server:",
        BASE_URL
    )

    print(
        "Agent Card:",
        BASE_URL
        + "/.well-known/agent-card.json"
    )

    uvicorn.run(
        app,
        host=HOST,
        port=PORT
    )
