EXAM_PROFILES = {
    "SSC JE 2026": {"technical": 100, "reasoning": 50, "gk": 50},
    "GATE CE": {"technical": 65}
}
QUESTION_TYPES = ["numerical","conceptual","statement","assertion_reason","match"]
DIFFICULTIES = ["easy","moderate","hard","very_hard"]

def exam_config(exam: str) -> dict:
    return EXAM_PROFILES.get(exam, {"technical": 100})
