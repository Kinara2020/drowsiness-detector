import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect("alerts.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            timestamp TEXT,
            ear REAL,
            mar REAL
        )
    """)
    conn.commit()
    conn.close()

def log_alert(alert_type, ear, mar):
    conn = sqlite3.connect("alerts.db")
    conn.execute(
        "INSERT INTO alerts (type, timestamp, ear, mar) VALUES (?, ?, ?, ?)",
        (alert_type, datetime.now().isoformat(), ear, mar)
    )
    conn.commit()
    conn.close()

def get_alerts(limit=20):
    conn = sqlite3.connect("alerts.db")
    rows = conn.execute(
        "SELECT type, timestamp, ear, mar FROM alerts ORDER BY id DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return [{"type": r[0], "timestamp": r[1], "ear": r[2], "mar": r[3]} for r in rows]