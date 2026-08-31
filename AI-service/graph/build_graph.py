from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.graph import END, START, StateGraph

from .constants import (
    ROUTE_ACTIVITY_RESOLVER,
    ROUTE_ANSWER,
    ROUTE_CHAT,
    ROUTE_CONFIRMATION,
    ROUTE_CONSULTATION_SAVER,
    ROUTE_DATA_QUERY,
    ROUTE_DETECTOR,
    ROUTE_EXTRACT,
    ROUTE_GENERATOR,
    ROUTE_PATIENT,
    ROUTE_PATIENT_EXTRACTOR,
    ROUTE_PATIENT_ORCHESTRATOR,
    ROUTE_PATIENT_RESOLVER,
    ROUTE_REPORT_EXTRACTOR,
    ROUTE_REPORT_SAVER,
)
from .nodes.answer_synthesizer import NODE_NAME as ANSWER_NODE
from .nodes.answer_synthesizer import answer_synthesizer_node
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
from .nodes.patient_resolver import NODE_NAME as PATIENT_RESOLVER_NODE
from .nodes.patient_resolver import patient_resolver_node
from .nodes.consultation_saver import NODE_NAME as CONSULTATION_SAVER_NODE
from .nodes.consultation_saver import consultation_saver_node
from .nodes.report_extractor import NODE_NAME as REPORT_EXTRACTOR_NODE
from .nodes.report_extractor import (
    report_extractor_node,
    route_after_report_extractor,
)
from .nodes.report_saver import NODE_NAME as REPORT_SAVER_NODE
from .nodes.report_saver import report_saver_node
from .nodes.data_query import NODE_NAME as DATA_QUERY_NODE
from .nodes.data_query import data_query_node, route_after_data_query
from .nodes.guard import NODE_NAME as GUARD_NODE
from .nodes.guard import guard_node, route_after_guard
from .state import AssistantState

CHECKPOINT_SERDE = JsonPlusSerializer(
    allowed_msgpack_modules=[
        ("graph.models.activity", "Activity"),
        ("graph.models.consultation", "Consultation"),
        ("graph.models.report_extraction", "ReportExtraction"),
        ("graph.models.patient_details", "PatientDetails"),
        ("graph.models.activity_query_result", "ActivityResult"),
        ("graph.models.patient_details", "PatientSummary"),
        ("graph.models.patient_history", "PatientHistory"),
    ]
)


def build_graph():
    builder = StateGraph(AssistantState)
    builder.add_node(GUARD_NODE, guard_node)
    builder.add_node(DETECTOR_NODE, detector_node)
    builder.add_node(EXTRACTOR_NODE, activity_extractor_node)
    builder.add_node(CONFIRMATION_NODE, confirmation_node)
    builder.add_node(GENERATOR_NODE, generator_node)
    builder.add_node(CONSULTATION_EXTRACTOR_NODE, consultation_extractor_node)
    builder.add_node(ACTIVITY_RESOLVER_NODE, activity_resolver_node)
    builder.add_node(ORCHESTRATOR_NODE, patient_orchestrator_node)
    builder.add_node(PATIENT_RESOLVER_NODE, patient_resolver_node)
    builder.add_node(CONSULTATION_SAVER_NODE, consultation_saver_node)
    builder.add_node(REPORT_EXTRACTOR_NODE, report_extractor_node)
    builder.add_node(REPORT_SAVER_NODE, report_saver_node)
    builder.add_node(DATA_QUERY_NODE, data_query_node)
    builder.add_node(ANSWER_NODE, answer_synthesizer_node)

    builder.add_edge(START, GUARD_NODE)
    builder.add_conditional_edges(
        GUARD_NODE,
        route_after_guard,
        {
            ROUTE_REPORT_EXTRACTOR: REPORT_EXTRACTOR_NODE,
            ROUTE_DETECTOR: DETECTOR_NODE,
            ROUTE_GENERATOR: GENERATOR_NODE,
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
            ROUTE_DATA_QUERY: DATA_QUERY_NODE,
        },
    )
    builder.add_conditional_edges(
        DATA_QUERY_NODE,
        route_after_data_query,
        {
            ROUTE_ANSWER: ANSWER_NODE,
            ROUTE_GENERATOR: GENERATOR_NODE,
        },
    )
    builder.add_edge(ANSWER_NODE, GENERATOR_NODE)
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
            ROUTE_PATIENT_RESOLVER: PATIENT_RESOLVER_NODE,
            ROUTE_CONSULTATION_SAVER: CONSULTATION_SAVER_NODE,
            ROUTE_GENERATOR: GENERATOR_NODE,
        },
    )
    builder.add_edge(CONSULTATION_EXTRACTOR_NODE, ORCHESTRATOR_NODE)
    builder.add_edge(PATIENT_RESOLVER_NODE, CONSULTATION_SAVER_NODE)
    builder.add_edge(CONSULTATION_SAVER_NODE, GENERATOR_NODE)
    builder.add_edge(CONFIRMATION_NODE, GENERATOR_NODE)
    builder.add_edge(GENERATOR_NODE, END)

    return builder.compile(checkpointer=InMemorySaver(serde=CHECKPOINT_SERDE))


# Compiled once at import time — the service layer invokes this shared instance
# rather than rebuilding the graph per request.
graph = build_graph()
