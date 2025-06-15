import sqlite3
from contextlib import closing

DB_NAME = 'bot_data.db'

def init_db():
    with closing(sqlite3.connect(DB_NAME)) as conn:
        with conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS stats (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    games_played INTEGER DEFAULT 0,
                    wins INTEGER DEFAULT 0
                )
            ''')

def update_stats(user_id: int, username: str, won: bool):
    with closing(sqlite3.connect(DB_NAME)) as conn:
        with conn:
            conn.execute('''
                INSERT INTO stats (user_id, username, games_played, wins)
                VALUES (?, ?, 1, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    games_played = games_played + 1,
                    wins = wins + ?
            ''', (user_id, username, int(won), int(won)))

def get_leaderboard(limit=10):
    with closing(sqlite3.connect(DB_NAME)) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT username, wins, games_played FROM stats
            ORDER BY wins DESC LIMIT ?
        ''', (limit,))
        return cursor.fetchall()
