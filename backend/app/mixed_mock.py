from .question_generator import generate_questions

REASONING_QUESTIONS = [
    {"section":"reasoning","subject":"Reasoning","topic":"Series","difficulty":"moderate","question_type":"conceptual","question":"Find the next number: 3, 8, 15, 24, 35, ?","options":["46","48","49","50"],"answer":"48","solution":"Differences are 5, 7, 9, 11; next difference is 13. So 35 + 13 = 48.","formula":"a(n)=n²+2n","concept":"Look for changing differences.","common_trap":"Using a constant difference.","exam_tip":"Check first and second differences before guessing a pattern."},
    {"section":"reasoning","subject":"Reasoning","topic":"Coding-Decoding","difficulty":"moderate","question_type":"conceptual","question":"If CIVIL is coded as DJWJM by shifting every letter one place forward, how is SOIL coded?","options":["TPJM","TPIL","TQJM","SPJM"],"answer":"TPJM","solution":"Shift S→T, O→P, I→J, L→M.","formula":"Next alphabet position","concept":"Apply the same transformation to each character.","common_trap":"Missing the shift on one letter.","exam_tip":"Write the alphabet sequence when needed."},
    {"section":"reasoning","subject":"Reasoning","topic":"Analogy","difficulty":"moderate","question_type":"conceptual","question":"Beam : Bending :: Column : ?","options":["Torsion","Buckling","Seepage","Filtration"],"answer":"Buckling","solution":"A beam is commonly associated with bending; a slender column is commonly associated with buckling.","formula":"—","concept":"Identify the dominant engineering phenomenon in the pair.","common_trap":"Choosing a general strength mode rather than the specific association.","exam_tip":"For analogy questions, preserve the relationship, not just the subject area."},
]

GK_QUESTIONS = [
    {"section":"gk","subject":"General Awareness","topic":"Indian Polity","difficulty":"moderate","question_type":"conceptual","question":"Which Part of the Constitution of India deals with Fundamental Duties?","options":["Part III","Part IV","Part IVA","Part V"],"answer":"Part IVA","solution":"Fundamental Duties are contained in Article 51A under Part IVA.","formula":"—","concept":"Part IVA contains Fundamental Duties.","common_trap":"Confusing Fundamental Duties with Directive Principles in Part IV.","exam_tip":"Remember: Part III = Fundamental Rights; Part IV = DPSP; Part IVA = Fundamental Duties."},
    {"section":"gk","subject":"General Awareness","topic":"Environment","difficulty":"moderate","question_type":"conceptual","question":"Which gas is commonly used as an indicator of acid rain formation?","options":["Sulfur dioxide","Helium","Hydrogen","Neon"],"answer":"Sulfur dioxide","solution":"Sulfur dioxide can oxidize and form sulfuric acid in atmospheric processes, contributing to acid deposition.","formula":"—","concept":"SO₂ is a major acid-rain precursor.","common_trap":"Confusing greenhouse gases with acid-rain precursors.","exam_tip":"Associate SO₂ and NOx with acid deposition."},
    {"section":"gk","subject":"General Awareness","topic":"Science","difficulty":"moderate","question_type":"conceptual","question":"The SI unit of dynamic viscosity is:","options":["Pa·s","N/m²","m²/s","N·m"],"answer":"Pa·s","solution":"Dynamic viscosity has SI unit pascal-second (Pa·s), equivalent to N·s/m².","formula":"τ = μ du/dy","concept":"Dynamic viscosity relates shear stress to velocity gradient.","common_trap":"m²/s is kinematic viscosity.","exam_tip":"Dynamic: Pa·s; kinematic: m²/s."},
]

def _clone(q):
    return dict(q, options=list(q["options"]))

def build_mixed_mock(technical_count=100, reasoning_count=50, gk_count=50):
    tech = []
    for subject in ["Strength of Material","Fluid Mechanics","Soil","Survey","Hydraulics"]:
        generated = generate_questions("SSC JE 2026", subject, "", "moderate", "numerical", 5)
        tech.extend(dict(q, section="technical") for q in generated)
    pool = tech + [_clone(q) for q in REASONING_QUESTIONS] + [_clone(q) for q in GK_QUESTIONS]
    def take(section, n):
        items=[q for q in pool if q.get("section")==section]
        if not items: return []
        return [dict(items[i % len(items)], id=f"{section}-{i+1}") for i in range(n)]
    return take("technical", technical_count)+take("reasoning", reasoning_count)+take("gk", gk_count)
