def trend_record(title, source, published_at, relevance, summary):
    return {"title":title,"source":source,"published_at":published_at,"relevance":relevance,"summary":summary}

def current_affairs_prompt(exam, date_context):
    return f"Find and summarize verified engineering, infrastructure, environment and policy developments relevant to {exam} as of {date_context}. Include source and date; do not invent current facts."
