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

PATIENT_MATCH_ANSWER_PROMPT = (
    "The doctor was just asked which of several existing patient records they "
    "mean, or whether this is a new patient. Given their reply below and the "
    "numbered candidate list, decide which candidate they mean.\n"
    "Set candidate_index to the matching candidate's number, or leave it null "
    "if the doctor means a new patient not in the list."
)
