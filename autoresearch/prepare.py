# prepare.py  —  DO NOT MODIFY (fixed evaluation harness)
# Equivalent of prepare.py in Karpathy's autoresearch.
# Scores the Laws of Simplicity SKILL.md against the 10 Laws framework.

import re
from pathlib import Path

SKILL_PATH = Path("skills/laws-of-simplicity/SKILL.md")

LAWS = [
    "REDUCE", "ORGANIZE", "TIME", "LEARN", "DIFFERENCES",
    "CONTEXT", "EMOTION", "TRUST", "FAILURE", "THE ONE",
]


def _has_section(text: str, heading: str) -> bool:
    return bool(re.search(rf"^#+\s+.*{re.escape(heading)}", text, re.MULTILINE | re.IGNORECASE))


def _has_law_with_actionable(text: str, law: str) -> bool:
    law_pattern = re.escape(law)
    has_mention = bool(re.search(rf"\b{law_pattern}\b", text, re.IGNORECASE))
    if not has_mention:
        return False
    actionable_patterns = [
        r"(?:ask|check|question|verify|ensure|consider|prioritize|focus|accept|create|optimize|group|remove|balance|learn|subtract)",
        r"(?:before|during|after)\s+\w+",
        r"(?:should|must|need to|always|never)",
        r"\?",
    ]
    match = re.search(rf"\b{law_pattern}\b", text, re.IGNORECASE)
    if not match:
        return False
    start = match.start()
    end = len(text)
    next_heading = re.search(r"\n#+\s", text[start + len(law):])
    if next_heading:
        end = start + len(law) + next_heading.start()
    section_text = text[start:end]
    return any(re.search(p, section_text, re.IGNORECASE) for p in actionable_patterns)


def score_core_laws(text: str) -> int:
    score = 0
    for law in LAWS:
        if _has_law_with_actionable(text, law):
            score += 4
    return score  # max 40


def score_decision_framework(text: str) -> int:
    score = 0
    if re.search(r"simplicity[_ ]delta|simplicity[_ ]score", text, re.IGNORECASE):
        score += 5
    if re.search(r"(?:keep|discard).*(?:if|when)", text, re.IGNORECASE):
        score += 5
    if re.search(r"crash.*(?:handl|log|root.cause|hypoth)", text, re.IGNORECASE):
        score += 5
    if re.search(r"(?:threshold|margin|>=|<=|>\s*\d|<\s*\d)", text):
        score += 5
    if re.search(r"trade.?off|all.else.being.equal|complexity.cost|complexity.*worth", text, re.IGNORECASE):
        score += 5
    return score  # max 25


def score_workflow_integration(text: str) -> int:
    score = 0
    if re.search(r"(?:before|beginning|start).*(?:task|experiment|work)", text, re.IGNORECASE):
        score += 4
    if re.search(r"(?:after|complet|end).*(?:task|experiment|reflect|review)", text, re.IGNORECASE):
        score += 4
    if re.search(r"self.?evolv|self.?improv|review.*every|trend", text, re.IGNORECASE):
        score += 4
    if re.search(r"results\.tsv|log.*result|record.*result", text, re.IGNORECASE):
        score += 4
    if re.search(r"trend|cumulative|last\s+\d+\s+(?:experiment|run)", text, re.IGNORECASE):
        score += 4
    return score  # max 20


def score_quality_clarity(text: str) -> int:
    score = 0
    example_count = len(re.findall(r"\*\*.*?\*\*.*?:", text))
    if example_count >= 5:
        score += 5
    elif example_count >= 3:
        score += 3
    if re.search(r"checklist|quick.reference|\- \[[ x]\]", text, re.IGNORECASE):
        score += 5
    if re.search(r"evidence.*before|verify.*before|trace.*before|confirm.*before", text, re.IGNORECASE):
        score += 5
    return score  # max 15


def evaluate():
    text = SKILL_PATH.read_text() if SKILL_PATH.exists() else ""
    d1 = score_core_laws(text)
    d2 = score_decision_framework(text)
    d3 = score_workflow_integration(text)
    d4 = score_quality_clarity(text)
    total = d1 + d2 + d3 + d4
    print(f"---")
    print(f"skill_conformance_score: {total}/100")
    print(f"  core_laws:            {d1}/40")
    print(f"  decision_framework:   {d2}/25")
    print(f"  workflow_integration: {d3}/20")
    print(f"  quality_clarity:      {d4}/15")
    return total


if __name__ == "__main__":
    evaluate()
