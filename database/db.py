import sqlite3

def backup_season_1(cursor):
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users_season1 AS
    SELECT * FROM users
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS matches_season1 AS
    SELECT * FROM matches
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_matches_season1 AS
    SELECT * FROM user_matches
    ''')

def init_db():
    conn = sqlite3.connect('civilwar_user.db')
    cursor = conn.cursor()
    
    # Backup existing data to season 1 tables
    backup_season_1(cursor)
    
    # Modify users table to add lol_puuid attribute
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        score INTEGER,
        top_score INTEGER,
        low_score INTEGER,
        lol_puuid TEXT,
        mvp_point INTEGER DEFAULT 0
    )
    ''')

    # Create new matches table for season 2
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
    
    # Create new user_matches table for season 2
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

# Initialize the database
conn, cursor = init_db()
conn.close()
