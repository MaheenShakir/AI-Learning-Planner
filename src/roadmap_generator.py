import json
import re
from datetime import date

from src.ai_assistant import ask_gemini

REQUIRED_KEYS = ["phase", "title", "description", "estimated_hours",
                 "practice", "mini_project", "resources"]


def available_hours(goal):
    """Total hours the learner can study before the target date."""
    days_left = (date.fromisoformat(goal["target_date"]) - date.today()).days
    weeks_left = max(days_left / 7, 1)
    return round(weeks_left * goal["days_per_week"] * goal["hours_per_day"], 1)


def build_prompt(goal, total_hours):
    return f"""Create a learning roadmap for this learner.

Goal: {goal['goal']}
Current level: {goal['level']}
Preferred learning style: {goal['learning_style']}
Total study hours available: {total_hours}

Rules:
- Return ONLY a JSON list. No explanation, no markdown fences.
- Use 3 to 4 phases, ordered from foundations to advanced.
- Use 8 to 14 topics in total, in the order they should be studied.
- The estimated_hours of all topics must add up to about {total_hours}.
- Start at the learner's level ({goal['level']}); do not repeat basics they already know.
- Each item must have exactly these keys:
  "phase" (string, e.g. "Phase 1: Foundations"),
  "title" (string),
  "description" (1-2 sentences),
  "estimated_hours" (number),
  "practice" (one practice exercise),
  "mini_project" (one small project for this topic),
  "resources" (2-3 free resources, as a string with one per line)
"""


def parse_roadmap(text):
    """Turn the AI's reply into a clean list of topic dicts."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)  # strip code fences
    start, end = text.find("["), text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError("The AI did not return a roadmap list.")
    items = json.loads(text[start:end + 1])

    topics = []
    for item in items:
        if not all(k in item for k in REQUIRED_KEYS):
            continue
        resources = item["resources"]
        if isinstance(resources, list):
            resources = "\n".join(str(r) for r in resources)
        topics.append({
            "phase": str(item["phase"]),
            "title": str(item["title"]),
            "description": str(item["description"]),
            "estimated_hours": float(item["estimated_hours"]),
            "practice": str(item["practice"]),
            "mini_project": str(item["mini_project"]),
            "resources": str(resources),
        })
    if not topics:
        raise ValueError("The roadmap was empty. Please try again.")
    return topics


def scale_hours(topics, total_hours):
    """Make sure the topic hours never add up to more than the time available."""
    planned = sum(t["estimated_hours"] for t in topics)
    if planned > total_hours and planned > 0:
        factor = total_hours / planned
        for t in topics:
            t["estimated_hours"] = round(t["estimated_hours"] * factor, 1)
    return topics


def generate_roadmap(goal):
    """Ask Gemini for a roadmap and return a list of topic dicts."""
    total_hours = available_hours(goal)
    reply = ask_gemini(build_prompt(goal, total_hours))
    topics = parse_roadmap(reply)
    return scale_hours(topics, total_hours)
