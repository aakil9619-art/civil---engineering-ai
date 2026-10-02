from dataclasses import dataclass
from typing import Literal

QuestionType = Literal["conceptual", "numerical", "statement", "assertion_reason", "match"]

@dataclass
class QuestionBlueprint:
    exam: str
    subject: str
    topic: str
    difficulty: str
    question_type: QuestionType

def build_blueprint(exam: str, subject: str, topic: str = "",
                    difficulty: str = "moderate",
                    question_type: QuestionType = "numerical") -> dict:
    return {
        "exam": exam,
        "subject": subject,
        "topic": topic,
        "difficulty": difficulty,
        "question_type": question_type,
        "rules": {
            "original_only": True,
            "show_solution": True,
            "show_concept": True,
            "include_common_trap": True,
            "include_exam_tip": True,
        },
    }
