from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.graph import END, START, StateGraph

from .constants import (
    ROUTE_ACTIVITY_DETAILS,
    ROUTE_ACTIVITY_DETAILS_GENERATOR,
    ROUTE_ACTIVITY_LOOKUP,
    ROUTE_ACTIVITY_RESOLVER,
    ROUTE_CHAT,
    ROUTE_CONFIRMATION,
    ROUTE_CONSULTATION_SAVER,
    ROUTE_DETECTOR,
    ROUTE_EXTRACT,
    ROUTE_GENERATOR,
    ROUTE_PATIENT,
    ROUTE_PATIENT_DETAILS,
    ROUTE_PATIENT_DETAILS_GENERATOR,
    ROUTE_PATIENT_EXTRACTOR,
    ROUTE_PATIENT_ORCHESTRATOR,
    ROUTE_REPORT_EXTRACTOR,
    ROUTE_REPORT_SAVER,
)
from .nodes.activity_confirmation import NODE_NAME as CONFIRMATION_NODE
from .nodes.activity_confirmation import confirmation_node
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
from .nodes.patient_orchestrator import NODE_NAME as ORCHESTRATOR_NODE
from .nodes.patient_orchestrator import (
    patient_orchestrator_node,
    route_after_orchestrator,
)
from .nodes.consultation_saver import NODE_NAME as CONSULTATION_SAVER_NODE
from .nodes.consultation_saver import consultation_saver_node
from .nodes.report_extractor import NODE_NAME as REPORT_EXTRACTOR_NODE
from .nodes.report_extractor import (
    report_extractor_node,
    route_after_report_extractor,
    route_entry,
)
from .nodes.report_saver import NODE_NAME as REPORT_SAVER_NODE
from .nodes.report_saver import report_saver_node
from .nodes.patient_details_fetcher import NODE_NAME as PATIENT_DETAILS_FETCHER_NODE
from .nodes.patient_details_fetcher import (
    patient_details_fetcher_node,
    route_after_patient_details_fetcher,
)
from .nodes.patient_details_generator import (
    NODE_NAME as PATIENT_DETAILS_GENERATOR_NODE,
)
from .nodes.patient_details_generator import patient_details_generator_node
from .nodes.activity_lookup import NODE_NAME as ACTIVITY_LOOKUP_NODE
from .nodes.activity_lookup import activity_lookup_node, route_after_activity_lookup
from .nodes.activity_details_generator import (
    NODE_NAME as ACTIVITY_DETAILS_GENERATOR_NODE,
)
from .nodes.activity_details_generator import activity_details_generator_node
from .state import AssistantState

# Explicitly allowlisted so checkpoint (de)serialization doesn't warn/block on
# our custom Activity model — see langgraph's LANGGRAPH_STRICT_MSGPACK gate.
CHECKPOINT_SERDE = JsonPlusSerializer(
    allowed_msgpack_modules=[
        ("graph.models.activity", "Activity"),
        ("graph.models.consultation", "Consultation"),
        ("graph.models.report_extraction", "ReportExtraction"),
        ("graph.models.patient_details", "PatientDetails"),
        ("graph.models.activity_details", "ActivityDetails"),
    ]
)


def build_graph():
    builder = StateGraph(AssistantState)
    builder.add_node(DETECTOR_NODE, detector_node)
    builder.add_node(EXTRACTOR_NODE, activity_extractor_node)
    builder.add_node(CONFIRMATION_NODE, confirmation_node)
    builder.add_node(GENERATOR_NODE, generator_node)
    builder.add_node(CONSULTATION_EXTRACTOR_NODE, consultation_extractor_node)
    builder.add_node(ACTIVITY_RESOLVER_NODE, activity_resolver_node)
    builder.add_node(ORCHESTRATOR_NODE, patient_orchestrator_node)
    builder.add_node(CONSULTATION_SAVER_NODE, consultation_saver_node)
    builder.add_node(REPORT_EXTRACTOR_NODE, report_extractor_node)
    builder.add_node(REPORT_SAVER_NODE, report_saver_node)
    builder.add_node(PATIENT_DETAILS_FETCHER_NODE, patient_details_fetcher_node)
    builder.add_node(PATIENT_DETAILS_GENERATOR_NODE, patient_details_generator_node)
    builder.add_node(ACTIVITY_LOOKUP_NODE, activity_lookup_node)
    builder.add_node(ACTIVITY_DETAILS_GENERATOR_NODE, activity_details_generator_node)

    builder.add_conditional_edges(
        START,
        route_entry,
        {
            ROUTE_REPORT_EXTRACTOR: REPORT_EXTRACTOR_NODE,
            ROUTE_DETECTOR: DETECTOR_NODE,
        },
    )
    builder.add_conditional_edges(
        REPORT_EXTRACTOR_NODE,
        route_after_report_extractor,
        {
            ROUTE_REPORT_SAVER: REPORT_SAVER_NODE,
            ROUTE_GENERATOR: GENERATOR_NODE,
        },
    )
    builder.add_edge(REPORT_SAVER_NODE, GENERATOR_NODE)
    builder.add_conditional_edges(
        DETECTOR_NODE,
        route_after_detector,
        {
            ROUTE_EXTRACT: EXTRACTOR_NODE,
            ROUTE_CHAT: GENERATOR_NODE,
            ROUTE_PATIENT: ORCHESTRATOR_NODE,
            ROUTE_PATIENT_DETAILS: PATIENT_DETAILS_FETCHER_NODE,
            ROUTE_ACTIVITY_DETAILS: ACTIVITY_LOOKUP_NODE,
        },
    )
    builder.add_conditional_edges(
        PATIENT_DETAILS_FETCHER_NODE,
        route_after_patient_details_fetcher,
        {
            ROUTE_GENERATOR: GENERATOR_NODE,
            ROUTE_PATIENT_DETAILS_GENERATOR: PATIENT_DETAILS_GENERATOR_NODE,
        },
    )
    builder.add_edge(PATIENT_DETAILS_GENERATOR_NODE, GENERATOR_NODE)
    builder.add_conditional_edges(
        ACTIVITY_LOOKUP_NODE,
        route_after_activity_lookup,
        {
            ROUTE_ACTIVITY_RESOLVER: ACTIVITY_RESOLVER_NODE,
            ROUTE_ACTIVITY_LOOKUP: ACTIVITY_LOOKUP_NODE,
            ROUTE_ACTIVITY_DETAILS_GENERATOR: ACTIVITY_DETAILS_GENERATOR_NODE,
            ROUTE_GENERATOR: GENERATOR_NODE,
        },
    )
    builder.add_edge(ACTIVITY_DETAILS_GENERATOR_NODE, GENERATOR_NODE)
    builder.add_conditional_edges(
        EXTRACTOR_NODE,
        route_after_activity_extractor,
        {ROUTE_CONFIRMATION: CONFIRMATION_NODE, ROUTE_GENERATOR: GENERATOR_NODE},
    )
    builder.add_conditional_edges(
        ORCHESTRATOR_NODE,
        route_after_orchestrator,
        {
            ROUTE_ACTIVITY_RESOLVER: ACTIVITY_RESOLVER_NODE,
            ROUTE_PATIENT_EXTRACTOR: CONSULTATION_EXTRACTOR_NODE,
            ROUTE_PATIENT_ORCHESTRATOR: ORCHESTRATOR_NODE,
            ROUTE_CONSULTATION_SAVER: CONSULTATION_SAVER_NODE,
            ROUTE_GENERATOR: GENERATOR_NODE,
        },
    )
    builder.add_edge(CONSULTATION_EXTRACTOR_NODE, ORCHESTRATOR_NODE)
    builder.add_edge(CONSULTATION_SAVER_NODE, GENERATOR_NODE)
    builder.add_edge(CONFIRMATION_NODE, GENERATOR_NODE)
    builder.add_edge(GENERATOR_NODE, END)

    # TODO: should check for writing in redis
    return builder.compile(checkpointer=InMemorySaver(serde=CHECKPOINT_SERDE))


# Compiled once at import time — the service layer invokes this shared instance
# rather than rebuilding the graph per request.
graph = build_graph()
