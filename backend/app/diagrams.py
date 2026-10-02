def simple_svg_diagram(title: str, labels: list[str]) -> str:
    safe_labels = "".join(
        f'<text x="40" y="{80 + i*28}" font-size="16">{label}</text>'
        for i, label in enumerate(labels)
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="700" height="320">
<rect x="1" y="1" width="698" height="318" fill="white" stroke="black"/>
<text x="40" y="40" font-size="22" font-weight="bold">{title}</text>
{safe_labels}
</svg>"""
