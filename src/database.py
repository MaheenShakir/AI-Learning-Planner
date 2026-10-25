import sqlite3
from datetime import datetime
from pathlib import Path

# data/planner.db, relative to the project root
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "planner.db"


def get_connection():
    """Open a connection to the database."""
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets us read columns by name
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create the tables if they don't exist yet."""
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT DEFAULT '',
                goal TEXT NOT NULL,
                level TEXT NOT NULL,
                hours_per_day REAL NOT NULL,
                days_per_week INTEGER NOT NULL,
                target_date TEXT NOT NULL,
                learning_style TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal_id INTEGER NOT NULL,
                phase TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                estimated_hours REAL,
                practice TEXT,
                mini_project TEXT,
                resources TEXT,
                position INTEGER,
                completed INTEGER DEFAULT 0,
                completed_at TEXT,
                FOREIGN KEY (goal_id) REFERENCES goals (id)
            );

            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal_id INTEGER NOT NULL,
                topic_id INTEGER,
                week_number INTEGER,
                day_label TEXT,
                objective TEXT,
                practice_activity TEXT,
                duration_hours REAL,
                completed INTEGER DEFAULT 0,
                completed_at TEXT,
                FOREIGN KEY (goal_id) REFERENCES goals (id),
                FOREIGN KEY (topic_id) REFERENCES topics (id)
            );
            """
        )
        # Older databases don't have user_id yet, so add it.
        columns = [row["name"] for row in conn.execute("PRAGMA table_info(goals)")]
        if "user_id" not in columns:
            conn.execute("ALTER TABLE goals ADD COLUMN user_id TEXT DEFAULT ''")


def save_goal(goal, level, hours_per_day, days_per_week, target_date,
              learning_style, user_id=""):
    """Save a new learning goal and return its id."""
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO goals
                (goal, level, hours_per_day, days_per_week,
                 target_date, learning_style, created_at, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (goal, level, hours_per_day, days_per_week,
             str(target_date), learning_style, datetime.now().isoformat(),
             user_id),
        )
        return cursor.lastrowid


def get_latest_goal(user_id=None):
    """Return the most recent goal for this visitor, or None.

    With no user_id it returns the latest goal of anyone (old behavior).
    """
    with get_connection() as conn:
        if user_id is None:
            row = conn.execute(
                "SELECT * FROM goals ORDER BY id DESC LIMIT 1"
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT * FROM goals WHERE user_id = ? ORDER BY id DESC LIMIT 1",
                (user_id,),
            ).fetchone()
        return dict(row) if row else None


def save_topics(goal_id, topics):
    """Save a list of roadmap topics (dicts) for a goal."""
    with get_connection() as conn:
        for position, t in enumerate(topics, start=1):
            conn.execute(
                """
                INSERT INTO topics
                    (goal_id, phase, title, description, estimated_hours,
                     practice, mini_project, resources, position)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (goal_id, t["phase"], t["title"], t["description"],
                 t["estimated_hours"], t["practice"], t["mini_project"],
                 t["resources"], position),
            )


def get_topics(goal_id):
    """Return all topics for a goal, in order, as a list of dicts."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM topics WHERE goal_id = ? ORDER BY position",
            (goal_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def delete_topics(goal_id):
    """Remove the roadmap (and its sessions) so a new one can be made."""
    with get_connection() as conn:
        conn.execute("DELETE FROM sessions WHERE goal_id = ?", (goal_id,))
        conn.execute("DELETE FROM topics WHERE goal_id = ?", (goal_id,))


def set_topic_completed(topic_id, completed):
    """Mark a topic done or not done."""
    with get_connection() as conn:
        conn.execute(
            "UPDATE topics SET completed = ?, completed_at = ? WHERE id = ?",
            (1 if completed else 0,
             datetime.now().isoformat() if completed else None,
             topic_id),
        )


def save_sessions(goal_id, sessions):
    """Save a list of study sessions (dicts) for a goal."""
    with get_connection() as conn:
        for s in sessions:
            conn.execute(
                """
                INSERT INTO sessions
                    (goal_id, topic_id, week_number, day_label, objective,
                     practice_activity, duration_hours)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (goal_id, s["topic_id"], s["week_number"], s["day_label"],
                 s["objective"], s["practice_activity"], s["duration_hours"]),
            )


def get_sessions(goal_id):
    """Return all study sessions for a goal, in order."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT s.*, t.title AS topic_title
            FROM sessions s
            LEFT JOIN topics t ON t.id = s.topic_id
            WHERE s.goal_id = ?
            ORDER BY s.id
            """,
            (goal_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def delete_sessions(goal_id):
    """Remove the schedule so a new one can be made."""
    with get_connection() as conn:
        conn.execute("DELETE FROM sessions WHERE goal_id = ?", (goal_id,))


def set_session_completed(session_id, completed):
    """Mark a study session done or not done."""
    with get_connection() as conn:
        conn.execute(
            "UPDATE sessions SET completed = ?, completed_at = ? WHERE id = ?",
            (1 if completed else 0,
             datetime.now().isoformat() if completed else None,
             session_id),
        )


if __name__ == "__main__":
    # Quick self-test: run `python src/database.py`
    init_db()
    print("Database created at:", DB_PATH)
    new_id = save_goal("Learn Python for Data Science", "Beginner", 2, 5, "2026-12-31", "Hands-on projects")
    print("Saved goal with id:", new_id)
    print("Latest goal:", get_latest_goal())
