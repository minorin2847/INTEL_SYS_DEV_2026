"""Request log (SQLite) and the /metrics aggregation.

Every screening is appended to `api/runtime/requests.sqlite`. `/metrics` shows what
actually happened over time; `/history` returns one session's screenings.
"""
from __future__ import annotations

import json
import sqlite3
import threading
import time
from typing import Optional

from . import config as C

_LOCK = threading.Lock()


def _conn() -> sqlite3.Connection:
    C.RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(C.REQUESTS_DB_PATH)
    con.execute(
        """CREATE TABLE IF NOT EXISTS screenings (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               ts REAL, session_id TEXT, age INTEGER, sex INTEGER,
               probability REAL, band TEXT, completeness REAL,
               bmi_capped INTEGER, low_completeness INTEGER,
               features_json TEXT, warnings_json TEXT)"""
    )
    return con


def log_screening(session_id: Optional[str], features: dict, result: dict) -> None:
    warnings = result.get("warnings", [])
    row = (
        time.time(), session_id or "anon",
        features.get("Age"), features.get("Sex"),
        result["probability"], result["band"], result["completeness"],
        int(any("BMI value capped" in w for w in warnings)),
        int(result["completeness"] < C.COMPLETENESS_WARN_BELOW),
        json.dumps(features), json.dumps(warnings),
    )
    with _LOCK:
        con = _conn()
        con.execute(
            """INSERT INTO screenings
               (ts, session_id, age, sex, probability, band, completeness,
                bmi_capped, low_completeness, features_json, warnings_json)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""", row)
        con.commit()
        con.close()


def history(session_id: str, limit: int = 50) -> list[dict]:
    with _LOCK:
        con = _conn()
        cur = con.execute(
            """SELECT ts, probability, band, completeness, features_json, warnings_json
               FROM screenings WHERE session_id = ? ORDER BY ts DESC LIMIT ?""",
            (session_id, limit))
        rows = cur.fetchall()
        con.close()
    return [{
        "ts": r[0], "probability": r[1], "band": r[2], "completeness": r[3],
        "features": json.loads(r[4]), "warnings": json.loads(r[5]),
    } for r in rows]


def metrics() -> dict:
    with _LOCK:
        con = _conn()
        n = con.execute("SELECT COUNT(*) FROM screenings").fetchone()[0]
        if not n:
            con.close()
            return {"n_screenings": 0}
        by_band = dict(con.execute(
            "SELECT band, COUNT(*) FROM screenings GROUP BY band").fetchall())
        flagged = con.execute(
            "SELECT COUNT(*) FROM screenings WHERE band = 'High'").fetchone()[0]
        capped = con.execute(
            "SELECT COUNT(*) FROM screenings WHERE bmi_capped = 1").fetchone()[0]
        thin = con.execute(
            "SELECT COUNT(*) FROM screenings WHERE low_completeness = 1").fetchone()[0]
        mean_completeness = con.execute(
            "SELECT AVG(completeness) FROM screenings").fetchone()[0]
        by_age = con.execute(
            """SELECT age, AVG(probability), COUNT(*) FROM screenings
               GROUP BY age ORDER BY age""").fetchall()
        con.close()
    return {
        "n_screenings": n,
        "flag_rate": round(flagged / n, 4),
        "band_distribution": {b: by_band.get(b, 0) for b in ("Low", "Moderate", "High")},
        "bmi_capped_rate": round(capped / n, 4),
        "low_completeness_rate": round(thin / n, 4),
        "mean_completeness": round(float(mean_completeness), 3),
        "mean_risk_by_age_band": [
            {"age": a, "mean_probability": round(p, 4), "n": c} for a, p, c in by_age],
    }
