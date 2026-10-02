# SSC JE 2026 Topic Blueprint
# Source: user's previously supplied SSC JE 2025 topic list/screenshot.
# These are the 36-topic coverage buckets to be incorporated into the generator.
# The engine should preserve the user's requested pattern:
# original questions, changed numerical data, reverse calculations, unit conversions,
# multi-step calculations, statement/option traps, and conceptual variants.

SSC_JE_2026_TOPIC_BUCKETS = [
    "Engineering Mechanics",
    "Strength of Material",
    "Structural Analysis",
    "Construction Management and Management",
    "Estimation Costing and Valuation",
    "RCC",
    "Steel",
    "Survey",
    "Soil",
    "Fluid Mechanics",
    "Hydraulics",
    "Hydrology",
    "Irrigation",
    "Environmental Engineering",
    "Transportation Engineering",
]

# The 36 detailed topics supplied previously are retained as the next expansion layer.
# Keep this registry extensible so the exact topic names can be appended without
# changing the API contract.
SSC_JE_2026_PATTERN_RULES = {
    "original_only": True,
    "numerical_variants": [
        "direct",
        "reverse",
        "changed_data",
        "multi_step",
        "unit_conversion",
    ],
    "question_types": [
        "numerical",
        "conceptual",
        "statement",
        "assertion_reason",
        "match",
    ],
    "difficulty_levels": ["easy", "moderate", "hard", "very_hard"],
    "include_solution": True,
    "include_formula": True,
    "include_concept": True,
    "include_common_trap": True,
    "include_exam_tip": True,
}
