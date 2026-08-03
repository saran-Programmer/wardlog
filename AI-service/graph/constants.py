from typing import Final

# Metadata key marking an AI message as a follow-up (asking for more info).
IS_FOLLOWUP_MESSAGE = "is_followup_message"

# Detector routes.
# Annotated Final (not just `= "..."`) so type checkers infer each constant's
# literal type, letting them be used inside Literal[...] type args elsewhere
# (e.g. RouteDecision.route in nodes/detector.py) instead of duplicating the
# raw string there.
ROUTE_EXTRACT: Final = "extract"
ROUTE_CHAT: Final = "chat"
ROUTE_PATIENT: Final = "patient"
ROUTE_ACTIVITY_RESOLVER: Final = "activity_resolver"
ROUTE_PATIENT_EXTRACTOR: Final = "patient_extractor"
ROUTE_PATIENT_ORCHESTRATOR: Final = "patient_orchestrator"
ROUTE_CONSULTATION_SAVER: Final = "consultation_saver"
ROUTE_GENERATOR: Final = "generator"
ROUTE_CONFIRMATION: Final = "confirmation"
ROUTE_DETECTOR: Final = "detector"
ROUTE_REPORT_EXTRACTOR: Final = "report_extractor"
ROUTE_REPORT_SAVER: Final = "report_saver"
ROUTE_PATIENT_DETAILS: Final = "patient_details"
ROUTE_PATIENT_DETAILS_GENERATOR: Final = "patient_details_generator"

# additional_kwargs key on a HumanMessage carrying a supplied document's path
# (dev CLI only — parsed from the `file (path): message` input format).
FILE_PATH_KEY = "file_path"

# Patient orchestrator: max number of activity candidates to present to the
# doctor for disambiguation before asking them to narrow the search instead.
MAX_DISAMBIGUATION_CANDIDATES = 5

# Resume choice sentinel: doctor sent a follow-up query instead of picking
# one of the presented activity candidates.
CHOICE_QUERY = "query"
