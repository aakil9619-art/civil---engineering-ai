def diagram_blueprint(subject, topic):
    t=(topic or "").lower()
    svg=""
    kind="generic"
    if any(x in t for x in ["beam","sfd","bmd","simply supported","cantilever"]):
        kind="beam"
        svg='''<svg viewBox="0 0 900 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Beam engineering diagram"><line x1="100" y1="150" x2="800" y2="150" stroke="currentColor" stroke-width="8"/><polygon points="180,150 145,210 215,210" fill="none" stroke="currentColor" stroke-width="4"/><circle cx="720" cy="205" r="35" fill="none" stroke="currentColor" stroke-width="4"/><line x1="400" y1="70" x2="400" y2="140" stroke="currentColor" stroke-width="4"/><polygon points="400,150 390,130 410,130" fill="currentColor"/><text x="370" y="55" font-size="24">P</text><text x="160" y="245" font-size="20">A</text><text x="700" y="245" font-size="20">B</text><text x="430" y="190" font-size="20">L</text></svg>'''
    elif any(x in t for x in ["pipe","bernoulli","continuity","flow"]):
        kind="pipe_flow"
        svg='''<svg viewBox="0 0 900 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Pipe flow diagram"><path d="M80 90 H350 L500 125 H820" fill="none" stroke="currentColor" stroke-width="55"/><line x1="100" y1="150" x2="300" y2="150" stroke="currentColor" stroke-width="4"/><polygon points="300,150 275,138 275,162" fill="currentColor"/><line x1="580" y1="150" x2="780" y2="150" stroke="currentColor" stroke-width="4"/><polygon points="780,150 755,138 755,162" fill="currentColor"/><text x="170" y="235" font-size="22">D₁, V₁</text><text x="610" y="235" font-size="22">D₂, V₂</text></svg>'''
    elif any(x in t for x in ["truss","frame"]):
        kind="truss"
        svg='''<svg viewBox="0 0 900 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Truss diagram"><g fill="none" stroke="currentColor" stroke-width="5"><line x1="120" y1="210" x2="780" y2="210"/><line x1="180" y1="210" x2="330" y2="80"/><line x1="330" y1="80" x2="480" y2="210"/><line x1="480" y1="210" x2="630" y2="80"/><line x1="630" y1="80" x2="780" y2="210"/><line x1="330" y1="80" x2="630" y2="80"/><line x1="330" y1="80" x2="480" y2="210"/><line x1="630" y1="80" x2="480" y2="210"/></g><polygon points="180,210 150,250 210,250" fill="none" stroke="currentColor" stroke-width="4"/><circle cx="720" cy="230" r="20" fill="none" stroke="currentColor" stroke-width="4"/></svg>'''
    elif any(x in t for x in ["level","levelling","survey"]):
        kind="levelling"
        svg='''<svg viewBox="0 0 900 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Levelling diagram"><line x1="90" y1="230" x2="810" y2="230" stroke="currentColor" stroke-width="3"/><line x1="180" y1="80" x2="180" y2="230" stroke="currentColor" stroke-width="8"/><line x1="700" y1="60" x2="700" y2="230" stroke="currentColor" stroke-width="8"/><line x1="130" y1="120" x2="750" y2="120" stroke="currentColor" stroke-width="4" stroke-dasharray="10 8"/><text x="120" y="260" font-size="22">BM / RL</text><text x="650" y="260" font-size="22">Point</text><text x="390" y="105" font-size="20">Line of sight</text></svg>'''
    else:
        kind="concept"
        svg='''<svg viewBox="0 0 900 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Civil engineering concept diagram"><rect x="150" y="80" width="600" height="140" rx="12" fill="none" stroke="currentColor" stroke-width="5"/><text x="450" y="145" text-anchor="middle" font-size="28">Civil Engineering Concept</text><text x="450" y="185" text-anchor="middle" font-size="20">Use the topic-specific labels and governing equation.</text></svg>'''
    return {"subject":subject,"topic":topic,"type":"svg","kind":kind,"svg":svg,"layers":["geometry","labels","loads_or_flow","dimensions"],"geometry":["main geometry","supports / boundaries"],"labels":["key points","variables","units"],"loads_or_flow":["applied load / flow direction"],"dimensions":["relevant length / diameter / level"],"status":"ready"}
