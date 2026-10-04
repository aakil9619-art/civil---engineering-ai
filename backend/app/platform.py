PROJECT_CATEGORIES = [
    "Structural Engineering","Geotechnical Engineering","Transportation Engineering",
    "Water Resources","Environmental Engineering","Construction Management",
    "Materials & Concrete","Surveying & Geomatics","Earthquake Engineering",
    "Smart Infrastructure","Renewable Energy & Infrastructure","Disaster Management"
]

def research_roadmap(topic: str, level: str = "B.Tech", budget: str = "Low", duration: str = "4 months") -> dict:
    topic = topic.strip() or "Civil Engineering"
    return {
        "topic": topic, "level": level, "budget": budget, "duration": duration,
        "path": [
            {"stage": 1, "title": "Define the problem", "deliverable": "Problem statement, motivation and scope"},
            {"stage": 2, "title": "Literature review", "deliverable": "Recent papers, methods, findings and limitations"},
            {"stage": 3, "title": "Find the research gap", "deliverable": "What is missing, inconsistent or not tested"},
            {"stage": 4, "title": "Research question & objectives", "deliverable": "1 primary question + measurable objectives"},
            {"stage": 5, "title": "Methodology", "deliverable": "Experimental, numerical, field or data-driven plan"},
            {"stage": 6, "title": "Resources & feasibility", "deliverable": "Materials, equipment, software, cost and schedule"},
            {"stage": 7, "title": "Data collection", "deliverable": "Measurements, simulations, surveys or datasets"},
            {"stage": 8, "title": "Analysis", "deliverable": "Calculations, modelling, statistics and validation"},
            {"stage": 9, "title": "Results & discussion", "deliverable": "Graphs, tables, interpretation and comparison"},
            {"stage": 10, "title": "Paper & presentation", "deliverable": "Report, references, slides and viva preparation"},
            {"stage": 11, "title": "Future work", "deliverable": "Limitations and realistic next research questions"}
        ],
        "checklist": [
            "Use primary research papers and official standards where appropriate.",
            "Record assumptions, units, datasets, software versions and test conditions.",
            "Do not fabricate experimental results or references.",
            "Verify codes, standards and safety-critical calculations with authoritative sources.",
            "Keep a research log so the project can be reproduced."
        ]
    }

def project_blueprint(title: str, level: str = "B.Tech", budget: str = "Low", duration: str = "4 months") -> dict:
    title = title.strip() or "Civil Engineering Project"
    return {
        "title": title, "level": level, "budget": budget, "duration": duration,
        "deliverables": [
            "Problem statement and objectives","Literature review","Methodology",
            "Work breakdown and timeline","Materials/equipment/software list",
            "Calculations or model","Drawings/diagrams","Results and discussion",
            "Cost/BOQ where relevant","Final report","Presentation","Viva questions"
        ],
        "workflow": ["Idea","Feasibility","Design","Execution/Simulation","Analysis","Documentation","Viva"]
    }
