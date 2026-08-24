from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.types import interrupt

from db.patient_search import search_patients

from ..config import DoctorContext
from ..constants import (
    INTERRUPT_PATIENT_MATCH,
    PATIENT_MATCH_AMBIGUOUS,
    PATIENT_MATCH_CLEAR,
    PATIENT_MATCH_NONE,
    PATIENT_MATCH_THRESHOLD,
)
from ..state import AssistantState
from .llm import get_llm

NODE_NAME = "patient_resolver"

PATIENT_MATCH_QUESTION_PROMPT = (
    "The doctor just described a patient, and more than one existing patient "
    "record could plausibly match. Write a short, conversational message "
    "listing the candidates, then ask the doctor which one they mean, or "
    "whether this is a new patient.\n"
    "List EVERY candidate as its own bullet point (one per line, starting "
    "with '- '), naming it using whatever distinguishing details are given "
    "below (name, age, sex) so the doctor can tell them apart.\n"
    "End with a short tail sentence explicitly asking the doctor to clarify "
    "which one they're referring to. Do not add anything beyond the "
    "candidate bullets and that closing question."
)


def _describe_candidate(candidate: dict) -> str:
    patient = candidate["patient"]
    details = []
    if patient.age is not None:
        details.append(f"age {patient.age}")
    if patient.sex:
        details.append(patient.sex)
    if details:
        return f"{patient.name} ({', '.join(details)})"
    return patient.name


def decide_patient_match(candidates: list[dict]) -> str:
    """Pure decision over ranked patient candidates — no LLM, no interrupt.

    `candidates` is the `search_patients` result: sorted descending by
    `match_percentage`, `[]` when nothing hit. See PATIENT_MATCH_THRESHOLD
    for the confidence cutoff.
    """
    if not candidates:
        return PATIENT_MATCH_NONE

    top_score = candidates[0]["match_percentage"]
    tied_for_top = [c for c in candidates if c["match_percentage"] == top_score]
    at_or_above_threshold = [
        c for c in candidates if c["match_percentage"] >= PATIENT_MATCH_THRESHOLD
    ]

    if (
        top_score < PATIENT_MATCH_THRESHOLD
        or len(tied_for_top) > 1
        or len(at_or_above_threshold) > 1
    ):
        return PATIENT_MATCH_AMBIGUOUS

    return PATIENT_MATCH_CLEAR


def _generate_match_question(candidates: list[dict]) -> str:
    candidate_lines = "\n".join(f"- {_describe_candidate(c)}" for c in candidates)
    response = get_llm(temperature=0.3).invoke(
        [
            SystemMessage(content=PATIENT_MATCH_QUESTION_PROMPT),
            SystemMessage(content=f"Candidates:\n{candidate_lines}"),
        ]
    )
    return response.content


def patient_resolver_node(state: AssistantState, config: RunnableConfig):
    doctor = DoctorContext(
        **{
            k: v
            for k, v in config["configurable"].items()
            if k in DoctorContext.model_fields
        }
    )
    patient = state["consultation"].patient

    candidates = search_patients(doctor.id, patient)
    case = decide_patient_match(candidates)

    if case == PATIENT_MATCH_NONE:
        return {
            "patient_candidates": candidates,
            "patient_match_case": case,
            "create_new_patient": True,
        }

    if case == PATIENT_MATCH_CLEAR:
        return {
            "patient_candidates": candidates,
            "patient_match_case": case,
            "resolved_patient_id": candidates[0]["patient"].id,
        }

    question = _generate_match_question(candidates)

    # Fires the interrupt and pauses the graph here. Parsing the doctor's
    # reply (resumed below), and the resulting link/create, is step 2 — not
    # implemented yet.
    interrupt({"type": INTERRUPT_PATIENT_MATCH, "question": question})

    return {
        "patient_candidates": candidates,
        "patient_match_case": case,
    }
