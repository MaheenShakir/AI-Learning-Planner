from datetime import date, timedelta


def study_dates(start, days_per_week):
    """Yield study dates forever, using the first N weekdays (Mon, Tue, ...)."""
    current = start
    while True:
        if current.weekday() < days_per_week:  # Mon=0 ... Sun=6
            yield current
        current += timedelta(days=1)


def build_schedule(goal, topics, start=None):
    """Spread the unfinished topics over study days.

    No day ever gets more than the learner's hours_per_day.
    Returns a list of session dicts.
    """
    start = start or date.today()
    daily_capacity = float(goal["hours_per_day"])

    days = study_dates(start, goal["days_per_week"])
    current_day = next(days)
    # Week 1 starts on the Monday of the first study day
    first_monday = current_day - timedelta(days=current_day.weekday())
    room_today = daily_capacity

    sessions = []
    for topic in topics:
        if topic["completed"]:
            continue

        # Cut this topic into pieces that fit into the days.
        remaining = round(float(topic["estimated_hours"] or 1), 2)
        pieces = []
        while remaining > 0.01:
            if room_today < 0.25:  # day is full, go to the next study day
                current_day = next(days)
                room_today = daily_capacity
            hours = round(min(remaining, room_today), 2)
            pieces.append((current_day, hours))
            remaining = round(remaining - hours, 2)
            room_today = round(room_today - hours, 2)

        for i, (day, hours) in enumerate(pieces):
            if len(pieces) == 1:
                objective = f"Learn and practice: {topic['title']}"
                activity = topic["practice"]
            elif i == 0:
                objective = f"Get started with: {topic['title']}"
                activity = "Go through the first resource and take notes."
            elif i == len(pieces) - 1:
                objective = f"Finish and apply: {topic['title']}"
                activity = topic["practice"]
            else:
                objective = f"Keep going with: {topic['title']}"
                activity = "Continue the resources and try small examples."

            week_number = (day - first_monday).days // 7 + 1
            sessions.append({
                "topic_id": topic["id"],
                "week_number": week_number,
                "day_label": day.strftime("%a %d %b"),
                "objective": objective,
                "practice_activity": activity,
                "duration_hours": hours,
                "date": day,
            })
    return sessions
