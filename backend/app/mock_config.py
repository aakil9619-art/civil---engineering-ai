from dataclasses import dataclass

@dataclass
class MockConfig:
    exam: str
    total_questions: int
    duration_minutes: int
    sections: dict

MOCKS={
 "SSC JE 2026": MockConfig("SSC JE 2026",200,120,{"technical":100,"reasoning":50,"gk":50}),
 "GATE CE": MockConfig("GATE CE",65,180,{"technical":65})
}
def get_mock_config(exam): return MOCKS.get(exam, MOCKS["SSC JE 2026"])
