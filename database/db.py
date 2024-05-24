import sqlite3

def init_db():
    conn = sqlite3.connect('civilwar_user.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        score INTEGER,
        top_score INTEGER,
        low_score INTEGER
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS matches (
        match_id INTEGER PRIMARY KEY AUTOINCREMENT,
        team1_username1 TEXT,
        team1_username2 TEXT,
        team1_username3 TEXT,
        team1_username4 TEXT,
        team1_username5 TEXT,
        team2_username1 TEXT,
        team2_username2 TEXT,
        team2_username3 TEXT,
        team2_username4 TEXT,
        team2_username5 TEXT,
        winner_team INTEGER,
        match_datetime TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_matches (
        username TEXT,
        match_id INTEGER,
        win_loss TEXT,
        match_datetime TEXT,
        FOREIGN KEY (username) REFERENCES users(username),
        FOREIGN KEY (match_id) REFERENCES matches(match_id),
        PRIMARY KEY (username, match_id)
    )
    ''')
    
    conn.commit()
    return conn, cursor

def get_db_connection():
    conn = sqlite3.connect('civilwar_user.db')
    cursor = conn.cursor()
    return conn, cursor
