from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.graph import END, START, StateGraph

from .constants import IS_FOLLOWUP_MESSAGE, ROUTE_CHAT, ROUTE_EXTRACT, ROUTE_PATIENT
from .nodes.confirmation import NODE_NAME as CONFIRMATION_NODE
from .nodes.confirmation import confirmation_node
from .nodes.detector import NODE_NAME as DETECTOR_NODE
from .nodes.detector import detector_node, route_after_detector
from .nodes.activity_extractor import NODE_NAME as EXTRACTOR_NODE
from .nodes.activity_extractor import (
    activity_extractor_node,
    route_after_activity_extractor,
)
from .nodes.generator import NODE_NAME as GENERATOR_NODE
from .nodes.generator import generator_node
from .nodes.consultation_extractor import NODE_NAME as CONSULTATION_EXTRACTOR_NODE
from .nodes.consultation_extractor import consultation_extractor_node
from .nodes.activity_resolver import NODE_NAME as ACTIVITY_RESOLVER_NODE
from .nodes.activity_resolver import activity_resolver_node
from .state import AssistantState

# Explicitly allowlisted so checkpoint (de)serialization doesn't warn/block on
# our custom Activity model — see langgraph's LANGGRAPH_STRICT_MSGPACK gate.
CHECKPOINT_SERDE = JsonPlusSerializer(
    allowed_msgpack_modules=[("graph.models.activity", "Activity")]
)


def build_graph():
    builder = StateGraph(AssistantState)
    builder.add_node(DETECTOR_NODE, detector_node)
    builder.add_node(EXTRACTOR_NODE, activity_extractor_node)
    builder.add_node(CONFIRMATION_NODE, confirmation_node)
    builder.add_node(GENERATOR_NODE, generator_node)
    builder.add_node(CONSULTATION_EXTRACTOR_NODE, consultation_extractor_node)
    builder.add_node(ACTIVITY_RESOLVER_NODE, activity_resolver_node)

    builder.add_edge(START, DETECTOR_NODE)
    builder.add_conditional_edges(
        DETECTOR_NODE,
        route_after_detector,
        {
            ROUTE_EXTRACT: EXTRACTOR_NODE,
            ROUTE_CHAT: GENERATOR_NODE,
            ROUTE_PATIENT: CONSULTATION_EXTRACTOR_NODE,
        },
    )
    builder.add_conditional_edges(
        EXTRACTOR_NODE,
        route_after_activity_extractor,
        {"confirmation": CONFIRMATION_NODE, "generator": GENERATOR_NODE},
    )
    builder.add_edge(CONFIRMATION_NODE, GENERATOR_NODE)
    builder.add_edge(CONSULTATION_EXTRACTOR_NODE, GENERATOR_NODE)
    builder.add_edge(ACTIVITY_RESOLVER_NODE, GENERATOR_NODE)
    builder.add_edge(GENERATOR_NODE, END)

    return builder.compile(checkpointer=InMemorySaver(serde=CHECKPOINT_SERDE))
