"""
Database and Persistence Manager for TypeStrike
Uses SQLite to store high scores, lifetime achievements, session history,
and user preferences safely.
"""

import os
import sqlite3
import datetime
from contextlib import contextmanager
from typing import List, Dict, Any, Optional
from src.config import DATA_DIR, DATABASE_PATH, DIFFICULTY_NORMAL, MODE_SURVIVAL


class DBManager:
    """Manages SQLite storage for high scores, historical analytics, and settings."""
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = DBManager()
        return cls._instance

    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        """Initializes tables if they do not exist."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # High scores table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS high_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mode TEXT NOT NULL,
                    difficulty TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    wpm REAL NOT NULL,
                    accuracy REAL NOT NULL,
                    survival_time REAL NOT NULL,
                    grade TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)

                # Detailed session history table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS session_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mode TEXT NOT NULL,
                    difficulty TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    net_wpm REAL NOT NULL,
                    peak_wpm REAL NOT NULL,
                    accuracy REAL NOT NULL,
                    completed_words INTEGER NOT NULL,
                    missed_words INTEGER NOT NULL,
                    longest_streak INTEGER NOT NULL,
                    survival_time REAL NOT NULL,
                    grade TEXT NOT NULL,
                    played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)

                # Settings table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """)
                conn.commit()
        except Exception as e:
            print(f"[DBManager] Database initialization error: {e}")

    def save_session(self, summary: Dict[str, Any], mode: str, difficulty: str) -> bool:
        """Saves a completed session into both history and high scores if eligible."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO session_history (
                    mode, difficulty, score, net_wpm, peak_wpm, accuracy,
                    completed_words, missed_words, longest_streak, survival_time, grade
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    mode,
                    difficulty,
                    int(summary.get("score", 0)),
                    float(summary.get("net_wpm", 0.0)),
                    float(summary.get("peak_wpm", 0.0)),
                    float(summary.get("accuracy", 0.0)),
                    int(summary.get("completed_words", 0)),
                    int(summary.get("missed_words", 0)),
                    int(summary.get("longest_streak", 0)),
                    float(summary.get("survival_time", 0.0)),
                    str(summary.get("grade", "D"))
                ))

                cursor.execute("""
                INSERT INTO high_scores (
                    mode, difficulty, score, wpm, accuracy, survival_time, grade
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    mode,
                    difficulty,
                    int(summary.get("score", 0)),
                    float(summary.get("net_wpm", 0.0)),
                    float(summary.get("accuracy", 0.0)),
                    float(summary.get("survival_time", 0.0)),
                    str(summary.get("grade", "D"))
                ))

                conn.commit()
                return True
        except Exception as e:
            print(f"[DBManager] Failed to save session: {e}")
            return False

    def get_top_scores(self, mode: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieves leaderboard entries ordered by highest score."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                if mode:
                    cursor.execute("""
                    SELECT * FROM high_scores 
                    WHERE mode = ? 
                    ORDER BY score DESC 
                    LIMIT ?
                    """, (mode, limit))
                else:
                    cursor.execute("""
                    SELECT * FROM high_scores 
                    ORDER BY score DESC 
                    LIMIT ?
                    """, (limit,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"[DBManager] Failed to fetch high scores: {e}")
            return []

    def get_lifetime_stats(self) -> Dict[str, Any]:
        """Calculates aggregated lifetime player stats across all recorded sessions."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                SELECT 
                    COUNT(*) as total_games,
                    COALESCE(MAX(score), 0) as high_score,
                    COALESCE(MAX(net_wpm), 0.0) as best_wpm,
                    COALESCE(AVG(accuracy), 0.0) as avg_accuracy,
                    COALESCE(SUM(completed_words), 0) as total_words_typed,
                    COALESCE(MAX(longest_streak), 0) as best_streak,
                    COALESCE(SUM(survival_time), 0.0) as total_time_played
                FROM session_history
                """)
                row = cursor.fetchone()
                if row:
                    return {
                        "total_games": row["total_games"],
                        "high_score": row["high_score"],
                        "best_wpm": round(row["best_wpm"], 1),
                        "avg_accuracy": round(row["avg_accuracy"], 1),
                        "total_words_typed": row["total_words_typed"],
                        "best_streak": row["best_streak"],
                        "total_time_played": round(row["total_time_played"] / 60.0, 1), # in minutes
                    }
        except Exception as e:
            print(f"[DBManager] Failed to fetch lifetime stats: {e}")

        return {
            "total_games": 0,
            "high_score": 0,
            "best_wpm": 0.0,
            "avg_accuracy": 0.0,
            "total_words_typed": 0,
            "best_streak": 0,
            "total_time_played": 0.0,
        }

    def set_setting(self, key: str, value: str):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
                conn.commit()
        except Exception as e:
            print(f"[DBManager] Error setting {key}: {e}")

    def get_setting(self, key: str, default: str = "") -> str:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
                row = cursor.fetchone()
                if row:
                    return row["value"]
        except Exception as e:
            print(f"[DBManager] Error getting {key}: {e}")
        return default
