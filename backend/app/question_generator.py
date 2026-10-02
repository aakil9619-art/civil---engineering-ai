from dataclasses import dataclass, asdict
from .seed_bank import generate_seed_questions
from typing import Literal
import random

QuestionType = Literal["conceptual", "numerical", "statement", "assertion_reason", "match"]

@dataclass
class Question:
    question: str
    options: list[str]
    answer: str
    solution: str
    formula: str
    concept: str
    common_trap: str
    exam_tip: str
    subject: str
    topic: str
    difficulty: str
    question_type: str

def _sample_som(subject: str, topic: str, difficulty: str, qtype: str) -> Question:
    return Question(
        question="A prismatic bar carries an axial tensile load P. If its length is doubled while area and material remain unchanged, how does the elastic elongation change?",
        options=["It becomes half", "It remains unchanged", "It becomes double", "It becomes four times"],
        answer="It becomes double",
        solution="For an axially loaded prismatic bar, delta = PL/(AE). With P, A and E unchanged, elongation is directly proportional to L. Therefore doubling L doubles elongation.",
        formula="delta = PL/(AE)",
        concept="Axial deformation is directly proportional to length and inversely proportional to area and Young's modulus.",
        common_trap="Do not confuse elongation with strain. Strain is delta/L and can remain unchanged when only L changes.",
        exam_tip="For proportional-change questions, write the governing equation first and cancel unchanged terms.",
        subject=subject, topic=topic or "Axial deformation", difficulty=difficulty, question_type=qtype
    )

def generate_questions(exam: str, subject: str, topic: str="", difficulty: str="moderate",
                       question_type: str="numerical", count: int=5) -> list[dict]:
    # Seed content is deliberately original and is used as a deterministic fallback.
    # Future LLM/RAG providers can replace this function without changing the API schema.
    seeded = generate_seed_questions(subject, topic, difficulty, question_type, count)
    if seeded:
        return seeded
    templates = [_sample_som(subject, topic, difficulty, question_type)]
    return [asdict(templates[i % len(templates)]) for i in range(count)]
