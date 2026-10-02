from dataclasses import dataclass

@dataclass
class MockResult:
    total: int
    attempted: int
    correct: int
    score: float
    accuracy: float
    avg_time_seconds: float

def calculate_result(total: int, answers: list[dict]) -> MockResult:
    attempted = len(answers)
    correct = sum(1 for a in answers if a.get("is_correct"))
    score = float(correct)
    accuracy = (correct / attempted * 100) if attempted else 0.0
    total_time = sum(float(a.get("time_seconds", 0)) for a in answers)
    avg_time = total_time / attempted if attempted else 0.0
    return MockResult(total, attempted, correct, score, accuracy, avg_time)
