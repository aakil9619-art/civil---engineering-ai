from dataclasses import dataclass, asdict

@dataclass(frozen=True)
class SeedQuestion:
    subject: str
    topic: str
    difficulty: str
    question_type: str
    question: str
    options: tuple[str, str, str, str]
    answer: str
    solution: str
    formula: str
    concept: str
    common_trap: str
    exam_tip: str

SEEDS = [
    SeedQuestion(
        "Strength of Material","Axial stress and strain","moderate","numerical",
        "A steel bar of length 2 m and area 500 mm² carries an axial tensile load of 50 kN. If E = 200 GPa, the elongation is:",
        ("0.5 mm","1.0 mm","2.0 mm","5.0 mm"),
        "1.0 mm",
        "delta = PL/(AE) = 50,000 x 2 / (500 x 10^-6 x 200 x 10^9) = 0.001 m = 1 mm.",
        "delta = PL/(AE)",
        "Elastic axial deformation depends directly on P and L and inversely on A and E.",
        "Mixing mm² with m² or GPa with Pa.",
        "Convert all quantities to consistent SI units before substitution."
    ),
    SeedQuestion(
        "Fluid Mechanics","Bernoulli equation","moderate","statement",
        "For steady, incompressible, frictionless flow along a streamline, which statement is correct?",
        ("Pressure head + velocity head + datum head is constant",
         "Pressure head alone is constant",
         "Velocity head is always zero",
         "Datum head must remain zero"),
        "Pressure head + velocity head + datum head is constant",
        "This is the energy equation for ideal steady flow along a streamline.",
        "p/(rho g) + V²/(2g) + z = constant",
        "Bernoulli's equation expresses conservation of mechanical energy under its stated assumptions.",
        "Applying the ideal form directly when significant head loss is present.",
        "Check the assumptions before selecting the Bernoulli form."
    ),
    SeedQuestion(
        "Soil","Effective stress","hard","conceptual",
        "A saturated soil layer is subjected to an increase in total vertical stress while pore-water pressure increases by the same amount. Neglecting other effects, the effective stress will:",
        ("Increase by the full stress increment","Decrease by the full stress increment",
         "Remain unchanged","Become zero"),
        "Remain unchanged",
        "Effective stress sigma' = sigma - u. Equal increases in total stress and pore pressure cancel.",
        "sigma' = sigma - u",
        "Effective stress governs the stress carried by the soil skeleton.",
        "Treating total stress and effective stress as interchangeable.",
        "Always compare the change in total stress with the change in pore pressure."
    ),
    SeedQuestion(
        "Survey","Levelling","moderate","numerical",
        "In levelling, a benchmark has RL = 100.000 m. The backsight is 1.250 m and the foresight is 2.000 m. The RL of the next point is:",
        ("99.250 m","100.750 m","101.250 m","103.250 m"),
        "99.250 m",
        "HI = RL + BS = 101.250 m. Next RL = HI - FS = 99.250 m.",
        "HI = RL + BS; RL = HI - FS",
        "Rise-and-fall/HI methods require consistent sign and sight conventions.",
        "Adding the foresight instead of subtracting it.",
        "For HI method: first calculate HI, then subtract FS."
    ),
    SeedQuestion(
        "Hydraulics","Continuity equation","easy","numerical",
        "Water flows through a pipe whose diameter changes from 200 mm to 100 mm. If velocity in the 200 mm section is 2 m/s, the velocity in the 100 mm section is:",
        ("1 m/s","2 m/s","4 m/s","8 m/s"),
        "8 m/s",
        "For incompressible steady flow, A1V1=A2V2. Area varies with D², so V2 = V1(D1/D2)² = 2(200/100)² = 8 m/s.",
        "A1V1 = A2V2",
        "For a circular pipe, A is proportional to D².",
        "Using the diameter ratio directly instead of squaring it.",
        "When diameter halves, velocity becomes four times for constant discharge."
    ),
]

def generate_seed_questions(subject: str, topic: str="", difficulty: str="moderate",
                            question_type: str="numerical", count: int=5) -> list[dict]:
    matches = [
        q for q in SEEDS
        if q.subject == subject
        and (not topic or topic.lower() in q.topic.lower())
        and (not difficulty or q.difficulty == difficulty)
        and (not question_type or q.question_type == question_type)
    ]
    if not matches:
        matches = [q for q in SEEDS if q.subject == subject] or SEEDS
    return [asdict(matches[i % len(matches)]) for i in range(min(count, 50))]
