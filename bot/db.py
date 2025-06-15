import sqlite3

conn = sqlite3.connect("stats.db")
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_stats (
        user_id INTEGER PRIMARY KEY,
        miner_wins INTEGER DEFAULT 0,
        coin_wins INTEGER DEFAULT 0,
        rps_wins INTEGER DEFAULT 0,
        guess_wins INTEGER DEFAULT 0
    )
''')

conn.commit()

def get_user_stats(user_id: int) -> dict:
    cursor.execute(
        "SELECT miner_wins, coin_wins, rps_wins, guess_wins FROM user_stats WHERE user_id = ?",
        (user_id,)
    )
    row = cursor.fetchone()
    if row is None:
        return {"miner_wins": 0, "coin_wins": 0, "rps_wins": 0, "guess_wins": 0}
    return {
        "miner_wins": row[0],
        "coin_wins": row[1],
        "rps_wins": row[2],
        "guess_wins": row[3],
    }

def increment_stat(user_id: int, column: str):
    if column not in ["miner_wins", "coin_wins", "rps_wins", "guess_wins"]:
        return
    cursor.execute("INSERT OR IGNORE INTO user_stats (user_id) VALUES (?)", (user_id,))
    cursor.execute(f"UPDATE user_stats SET {column} = {column} + 1 WHERE user_id = ?", (user_id,))
    conn.commit()

