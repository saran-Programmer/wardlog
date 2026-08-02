# Metadata key marking an AI message as a follow-up (asking for more info).
IS_FOLLOWUP_MESSAGE = "is_followup_message"

# Detector routes.
ROUTE_EXTRACT = "extract"
ROUTE_CHAT = "chat"
ROUTE_PATIENT = "patient"
ROUTE_ACTIVITY_RESOLVER = "activity_resolver"
ROUTE_PATIENT_EXTRACTOR = "patient_extractor"
ROUTE_PATIENT_ORCHESTRATOR = "patient_orchestrator"
ROUTE_CONSULTATION_SAVER = "consultation_saver"
ROUTE_GENERATOR = "generator"
ROUTE_CONFIRMATION = "confirmation"

# Patient orchestrator: max number of activity candidates to present to the
# doctor for disambiguation before asking them to narrow the search instead.
MAX_DISAMBIGUATION_CANDIDATES = 5

# Resume choice sentinel: doctor sent a follow-up query instead of picking
# one of the presented activity candidates.
CHOICE_QUERY = "query"
