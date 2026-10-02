from dataclasses import dataclass

@dataclass
class MockConfig:
    exam: str
    total_questions: int
    duration_minutes: int
    sections: dict
    negative_marking: float

MOCKS={
 "SSC JE 2026": MockConfig("SSC JE 2026",200,120,{"technical":100,"reasoning":50,"gk":50},0.25),
 "SSC JE Paper-II 2026": MockConfig("SSC JE Paper-II 2026",100,120,{"technical":100},1.0),
 "GATE CE": MockConfig("GATE CE",65,180,{"technical":65},0.0)
}
def get_mock_config(exam): return MOCKS.get(exam, MOCKS["SSC JE 2026"])
