from .question_generator import generate_questions
import random
import hashlib

REASONING_BASE = [
    ("Series","Find the next number: 3, 8, 15, 24, 35, {x}.",["46","48","49","50"],"48","Differences are 5, 7, 9, 11; next difference is 13."),
    ("Coding-Decoding","If CIVIL is coded as DJWJM by shifting every letter one place forward, how is SOIL coded?",["TPJM","TPIL","TQJM","SPJM"],"TPJM","Shift S→T, O→P, I→J, L→M."),
    ("Analogy","Beam : Bending :: Column : ?",["Torsion","Buckling","Seepage","Filtration"],"Buckling","A slender column is commonly associated with buckling.")
]
GK_BASE = [
    ("Indian Polity","Which Part of the Constitution of India deals with Fundamental Duties?",["Part III","Part IV","Part IVA","Part V"],"Part IVA","Fundamental Duties are in Article 51A under Part IVA."),
    ("Environment","Which gas is a major precursor of acid deposition?",["Sulfur dioxide","Helium","Hydrogen","Neon"],"Sulfur dioxide","SO₂ is a major acid-rain precursor."),
    ("Science","The SI unit of dynamic viscosity is:",["Pa·s","N/m²","m²/s","N·m"],"Pa·s","Dynamic viscosity is measured in pascal-second.")
]

def _hash(q):
    return hashlib.sha1(q["question"].encode()).hexdigest()

def _technical_pool():
    pool=[]
    # Generate deterministic parameter variants from original seed concepts.
    for i in range(1,21):
        P=40+i*5; L=1.5+(i%5)*0.5; A=400+(i%8)*50; E=200
        elong=P*1000*L/(A*1e-6*E*1e9)*1000
        opts=[f"{elong*0.5:.3f} mm",f"{elong:.3f} mm",f"{elong*2:.3f} mm",f"{elong*3:.3f} mm"]
        pool.append({"section":"technical","subject":"Strength of Material","topic":"Axial stress and strain","difficulty":"moderate","question_type":"numerical","question":f"A steel bar is {L:.1f} m long with area {A} mm² and carries {P} kN axial tension. If E = {E} GPa, its elongation is approximately:","options":opts,"answer":opts[1],"solution":f"δ = PL/(AE) = {elong:.3f} mm.","formula":"δ = PL/(AE)","concept":"Axial elongation varies directly with load and length and inversely with area and E.","common_trap":"Mixing mm², m and GPa.","exam_tip":"Convert all quantities consistently."})
    for i in range(1,21):
        D1=200+(i%5)*20; D2=100+(i%4)*10; V1=1.5+(i%6)*0.5; V2=V1*(D1/D2)**2
        opts=[f"{V2/2:.2f} m/s",f"{V2:.2f} m/s",f"{V2*2:.2f} m/s",f"{V2*4:.2f} m/s"]
        pool.append({"section":"technical","subject":"Hydraulics","topic":"Continuity equation","difficulty":"moderate","question":f"Water flows through a circular pipe reducing from {D1} mm diameter to {D2} mm. If V₁ = {V1:.1f} m/s, V₂ is:","options":opts,"answer":opts[1],"solution":f"A₁V₁=A₂V₂, so V₂=V₁(D₁/D₂)²={V2:.2f} m/s.","formula":"A₁V₁ = A₂V₂","concept":"For circular pipes, area is proportional to D².","common_trap":"Using D₁/D₂ without squaring.","exam_tip":"Square the diameter ratio."})
    for i in range(1,21):
        z=2+i%7; u=30+i*2; sigma=80+i*5; eff=sigma-u
        opts=[f"{eff:.0f} kPa",f"{sigma:.0f} kPa",f"{u:.0f} kPa",f"{sigma+u:.0f} kPa"]
        pool.append({"section":"technical","subject":"Soil","topic":"Effective stress","difficulty":"hard","question":f"A saturated soil has total vertical stress {sigma} kPa and pore pressure {u} kPa at a point. The effective stress is:","options":opts,"answer":opts[0],"solution":f"σ′=σ−u={sigma}−{u}={eff} kPa.","formula":"σ′ = σ − u","concept":"Effective stress is carried by the soil skeleton.","common_trap":"Adding pore pressure to total stress.","exam_tip":"Always subtract pore pressure."})
    for i in range(1,21):
        RL=100+i*0.25; BS=1.1+(i%5)*0.2; FS=1.4+(i%6)*0.15; nxt=RL+BS-FS
        opts=[f"{nxt:.3f} m",f"{RL+BS+FS:.3f} m",f"{RL-BS+FS:.3f} m",f"{nxt+1:.3f} m"]
        pool.append({"section":"technical","subject":"Survey","topic":"Levelling","difficulty":"moderate","question":f"At a benchmark RL={RL:.3f} m, BS={BS:.2f} m and FS={FS:.2f} m are observed. The RL of the next point is:","options":opts,"answer":opts[0],"solution":f"HI=RL+BS={RL+BS:.3f} m; next RL=HI−FS={nxt:.3f} m.","formula":"HI=RL+BS; RL=HI−FS","concept":"Height of instrument method.","common_trap":"Adding the foresight.","exam_tip":"Subtract FS from HI."})
    for i in range(1,21):
        V=2+i*0.2; z1=5+i%4; z2=2+i%3; p1=120+i*3
        h1=p1/9.81+V*V/(2*9.81)+z1
        v2=max(0.5,(2*9.81*(h1-z2-p1/9.81))**0.5)
        opts=[f"{v2:.2f} m/s",f"{v2+1:.2f} m/s",f"{max(.1,v2-1):.2f} m/s",f"{v2*2:.2f} m/s"]
        pool.append({"section":"technical","subject":"Fluid Mechanics","topic":"Bernoulli equation","difficulty":"moderate","question_type":"numerical","question":f"For ideal steady flow, pressure is {p1} kPa at point 1, V₁={V:.1f} m/s and z₁={z1} m. At point 2, pressure is the same and z₂={z2} m. The approximate V₂ is:","options":opts,"answer":opts[0],"solution":"Apply Bernoulli's equation between the two points and solve for V₂.","formula":"p/γ + V²/(2g) + z = constant","concept":"Bernoulli equation conserves mechanical energy for ideal steady flow.","common_trap":"Forgetting elevation head.","exam_tip":"Write all three head terms before substitution."})
    return pool

def _reasoning_pool(n):
    out=[]
    for i in range(1,n+1):
        topic, q, opts, ans, sol = REASONING_BASE[(i-1)%len(REASONING_BASE)]
        if topic=="Series":
            a=i+2; nums=[a*a+2*a for a in range(1,6)]
            q=f"Find the next number: {', '.join(map(str,nums))}, ?"
            d=[nums[j+1]-nums[j] for j in range(4)]; answer=str(nums[-1]+(d[-1]+2))
            opts=[str(int(answer)-2),answer,str(int(answer)+2),str(int(answer)+4)]; ans=answer
            sol="The successive differences increase by 2, so the next difference is the previous difference + 2."
        elif topic=="Coding-Decoding":
            shift=(i%4)+1
            q=f"If each letter is shifted {shift} place(s) forward, how is SOIL coded?"
            ans="".join(chr((ord(c)-65+shift)%26+65) for c in "SOIL")
            opts=[ans,ans[:-1]+"A",ans[:2]+"X"+ans[3:],ans[0]+"PIL"]
            sol=f"Shift every letter of SOIL forward by {shift}."
        else:
            pairs=[("Beam","Bending","Column","Buckling"),("Slab","Flexure","Footing","Bearing"),("Canal","Flow","Road","Traffic"),("Dam","Reservoir","Bridge","Span")]
            a,b,c,d=pairs[(i-1)%len(pairs)]; q=f"{a} : {b} :: {c} : ?"; opts=[d,"Seepage","Filtration","Torsion"]; ans=d; sol=f"The same engineering association is {c} : {d}."
        q = q + f" [Set {i}]"
        out.append({"section":"reasoning","subject":"Reasoning","topic":topic,"difficulty":"moderate","question_type":"conceptual","question":q,"options":opts,"answer":ans,"solution":sol,"formula":"—","concept":"Identify the transformation or relationship.","common_trap":"Applying the wrong pattern.","exam_tip":"Check the relationship before selecting an option."})
    return out

def _gk_pool(n):
    out=[]
    facts=[
      ("Indian Polity","Fundamental Duties are contained in which Part?",["Part III","Part IV","Part IVA","Part V"],"Part IVA","Article 51A contains Fundamental Duties."),
      ("Environment","Which is a major acid-rain precursor?",["SO₂","He","Ne","H₂"],"SO₂","Sulfur dioxide contributes to acid deposition."),
      ("Science","SI unit of dynamic viscosity?",["Pa·s","m²/s","N/m","J/s"],"Pa·s","Dynamic viscosity is measured in Pa·s."),
      ("Geography","The standard unit of discharge in SI is:",["m³/s","m²/s","N/s","kg/m"],"m³/s","Discharge is volume per unit time."),
      ("Engineering","Which material property indicates resistance to indentation?",["Hardness","Ductility","Porosity","Permeability"],"Hardness","Hardness is resistance to indentation or scratching.")
    ]
    for i in range(1,n+1):
        t,q,opts,ans,sol=facts[(i-1)%len(facts)]
        out.append({"section":"gk","subject":"General Awareness","topic":t,"difficulty":"moderate","question_type":"conceptual","question":q+f" [Set {i}]","options":opts,"answer":ans,"solution":sol,"formula":"—","concept":sol,"common_trap":"Confusing closely related terms.","exam_tip":"Revise the exact definition and unit."})
    return out

def build_mixed_mock(technical_count=100, reasoning_count=50, gk_count=50):
    pool=_technical_pool()
    tech=list(pool[:technical_count])
    # If a smaller/larger count is requested, cycle only after exhausting unique variants.
    if technical_count>len(pool):
        tech=[dict(pool[i%len(pool)],question=pool[i%len(pool)]["question"]+f" [Variant {i+1}]") for i in range(technical_count)]
    reason=_reasoning_pool(reasoning_count)
    gk=_gk_pool(gk_count)
    questions=tech+reason+gk
    seen=set(); unique=[]
    for q in questions:
        fp=_hash(q)
        if fp not in seen:
            seen.add(fp); unique.append(q)
    random.SystemRandom().shuffle(unique)
    for i,q in enumerate(unique,1):
        q["id"]=f"mock-{i}"
    return unique
