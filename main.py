import discord
from discord.ext import commands
import sqlite3
import itertools
import random
import logging
from datetime import datetime
import os

TOKEN = os.environ.get("DISCORD_TOKEN")

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
handler = logging.FileHandler(filename=f'logs/{datetime.now().strftime("%Y-%m-%d")}.log', encoding='utf-8', mode='a+')
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

intents = discord.Intents.default()  # bot이 사용할 기능 관련
intents.message_content = True  # 사용자 입력에 따라 작동하는 것을 하기 위해
bot = commands.Bot(command_prefix='!!', intents=intents)  # bot의 작동 prefix

# SQLite 데이터베이스 연결
conn = sqlite3.connect('civilwar_user.db')
cursor = conn.cursor()

# 사용자 테이블 생성
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    score INTEGER
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

@bot.event
async def on_ready():
    logger.info('다음으로 로그인')
    logger.info(bot.user.name)
    logger.info('connection was successful')
    await bot.change_presence(status=discord.Status.online, activity=None)

@bot.command(name="테스트")
async def test(ctx, text):
    await ctx.send(text)

# !addinfo 명령어: 사용자 정보를 추가하는 명령어
@bot.command(name='사용자추가')
async def add_info(ctx, username: str,  score: int):
    # SQLite에 사용자 정보 삽입
    cursor.execute('INSERT OR REPLACE INTO users (username, score) VALUES (?, ?)', (username, score))
    conn.commit()
    await ctx.send(f'사용자 정보를 추가했습니다: {username}, {score}')
    logger.info(f'사용자 정보를 추가했습니다: {username}, {score}')

# !모든사용자정보 명령어: 모든 사용자의 이름과 점수를 확인하는 명령어
@bot.command(name='모든사용자')
async def all_user_info(ctx):
    all_info = []
    # 모든 사용자 정보 조회
    cursor.execute('SELECT * FROM users')
    rows = cursor.fetchall()
    for row in rows:
        user_info_str = f'name: {row[0]},  Score: {row[1]}'
        all_info.append(user_info_str)

    if all_info:
        await ctx.send('\n'.join(all_info))
    else:
        await ctx.send('등록된 사용자 정보가 없습니다.')

team1_scores = {}
team2_scores = {}

@bot.command(name='팀나누기')
async def random_team_split(ctx, *users):
    global team1_scores, team2_scores
    
    if len(users) != 10:
        await ctx.send('10명의 사용자 이름을 입력해주세요.')
        return

    # 사용자의 이름과 점수를 저장할 딕셔너리
    user_scores = {}

    # 사용자 이름에 해당하는 점수를 가져와서 딕셔너리에 저장
    for username in users:
        cursor.execute('SELECT score FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        if row:
            user_scores[username] = row[0]
        else:
            await ctx.send(f'{username}의 점수를 찾을 수 없습니다.')
            return

    # 가능한 모든 팀 구성 생성
    all_team_compositions = list(itertools.combinations(user_scores.items(), len(users) // 2))

    # 최소 총합 점수 차이 구하기
    min_score_diff = float('inf')
    best_team_compositions = []
    for team_composition in all_team_compositions:
        team1 = team_composition
        team2 = [(username, score) for username, score in user_scores.items() if (username, score) not in team_composition]

        # 팀 점수 계산
        team1_score = sum(score for _, score in team1)
        team2_score = sum(score for _, score in team2)

        # 팀 점수의 차이 계산
        score_diff = abs(team1_score - team2_score)

        # 최소 총합 점수 차이 갱신
        if score_diff < min_score_diff:
            min_score_diff = score_diff
            best_team_compositions = [(team1, team2)]
        elif score_diff == min_score_diff:
            best_team_compositions.append((team1, team2))

    # 최소 총합 점수 차이를 가지는 팀 구성들 중 랜덤하게 선택
    chosen_team_composition = random.choice(best_team_compositions)
    team1, team2 = chosen_team_composition

    # 선택된 팀의 점수 계산
    team1_score = sum(score for _, score in team1)
    team2_score = sum(score for _, score in team2)
    
    team1_scores = dict(team1)
    team2_scores = dict(team2)

    # team1과 team2의 점수를 오름차순으로 정렬
    team1_sorted = sorted(team1, key=lambda x: x[1])
    team2_sorted = sorted(team2, key=lambda x: x[1])

    await ctx.send(f'Team 1 (Score: {team1_score}):\n{[f"{user[0]}: {user[1]}" for user in team1_sorted]}\n\nTeam 2 (Score: {team2_score}):\n{[f"{user[0]}: {user[1]}" for user in team2_sorted]}\n\nScore Difference: {min_score_diff}')
    logger.info(f'Team 1 (Score: {team1_score}):\n{[f"{user[0]}: {user[1]}" for user in team1_sorted]}\n\nTeam 2 (Score: {team2_score}):\n{[f"{user[0]}: {user[1]}" for user in team2_sorted]}\n\nScore Difference: {min_score_diff}')

@bot.command(name='팀1승리')
async def team1_win(ctx):
    global team1_scores, team2_scores
    if len(team1_scores) == 0:
        await ctx.send("팀부터 나눠라")
        return
    
    # 경기 종료 시각
    match_end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 팀 1이 승리한 경우
    winner_team = 1

    for username, score in team1_scores.items():
        cursor.execute('UPDATE users SET score = score + 1 WHERE username = ?', (username,))
    for username, score in team2_scores.items():
        cursor.execute('UPDATE users SET score = score - 1 WHERE username = ?', (username,))
    conn.commit()

    # 매치 정보 추가
    cursor.execute('INSERT INTO matches (team1_username1, team1_username2, team1_username3, team1_username4, team1_username5, '
                   'team2_username1, team2_username2, team2_username3, team2_username4, team2_username5, '
                   'winner_team, match_datetime) '
                   'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                   (*team1_scores.keys(), *team2_scores.keys(), winner_team, match_end_time))
    conn.commit()

    # 매치 ID 가져오기
    match_id = cursor.lastrowid
    
    # 중간 테이블에 사용자, 매치 ID, 승패 정보, 매치 시간 추가
    for username, score in team1_scores.items():
        cursor.execute('INSERT INTO user_matches (username, match_id, win_loss, match_datetime) VALUES (?, ?, ?, ?)', 
                       (username, match_id, 'win', match_end_time))
    for username, score in team2_scores.items():
        cursor.execute('INSERT INTO user_matches (username, match_id, win_loss, match_datetime) VALUES (?, ?, ?, ?)', 
                       (username, match_id, 'loss', match_end_time))

    team1_scores = {}
    team2_scores = {}
    
    await ctx.send('팀 1이 승리했습니다!')
    logger.info('팀 1이 승리했습니다!')

@bot.command(name='팀2승리')
async def team2_win(ctx):
    global team1_scores, team2_scores
    if len(team1_scores) == 0:
        await ctx.send("팀부터 나눠라")
        return
    
    # 경기 종료 시각
    match_end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 팀 2이 승리한 경우
    winner_team = 2

    for username, score in team1_scores.items():
        cursor.execute('UPDATE users SET score = score - 1 WHERE username = ?', (username,))
    for username, score in team2_scores.items():
        cursor.execute('UPDATE users SET score = score + 1 WHERE username = ?', (username,))
    conn.commit()

    # 매치 정보 추가
    cursor.execute('INSERT INTO matches (team1_username1, team1_username2, team1_username3, team1_username4, team1_username5, '
                   'team2_username1, team2_username2, team2_username3, team2_username4, team2_username5, '
                   'winner_team, match_datetime) '
                   'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                   (*team1_scores.keys(), *team2_scores.keys(), winner_team, match_end_time))
    conn.commit()

    # 매치 ID 가져오기
    match_id = cursor.lastrowid
    
    # 중간 테이블에 사용자, 매치 ID, 승패 정보, 매치 시간 추가
    for username, score in team1_scores.items():
        cursor.execute('INSERT INTO user_matches (username, match_id, win_loss, match_datetime) VALUES (?, ?, ?, ?)', 
                       (username, match_id, 'loss', match_end_time))
    for username, score in team2_scores.items():
        cursor.execute('INSERT INTO user_matches (username, match_id, win_loss, match_datetime) VALUES (?, ?, ?, ?)', 
                       (username, match_id, 'win', match_end_time))

    team1_scores = {}
    team2_scores = {}
    
    await ctx.send('팀 2가 승리했습니다!')
    logger.info('팀 2가 승리했습니다!')

@bot.command(name='점수수정')
async def modify_info(ctx, username: str, score: int):
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    row = cursor.fetchone()
    if row:
        cursor.execute('UPDATE users SET score = ? WHERE username = ?', (score, username,))
        conn.commit()
        await ctx.send(f'{username}의 정보가 수정되었습니다.')
        logger.info(f'{ctx.author.name}님이 {username}의 정보를 수정했습니다. ({score})')
    else:
        await ctx.send(f'{username}은(는) 등록되지 않은 사용자입니다.')
        logger.info(f'{ctx.author.name}님이 존재하지 않는 사용자의 정보를 수정하려고 시도했습니다.')


@bot.command(name='최근매치')
async def check_recent_team(ctx):
# 가장 최근에 등록된 5개의 경기 정보를 가져옵니다.
    cursor.execute('SELECT * FROM matches ORDER BY match_datetime DESC LIMIT 5')
    rows = cursor.fetchall()

    if rows:
        for row in rows:
            match_datetime = row[12]  # match_datetime 열의 인덱스를 가정합니다. 실제 인덱스에 맞게 수정해야 합니다.
            
            # 승자 팀과 패자 팀을 비교하여 각 팀의 플레이어들을 구분합니다.
            winner_team = row[11]  # winner_team 열의 인덱스를 가정합니다. 실제 인덱스에 맞게 수정해야 합니다.
            if winner_team == 1:
                winners = [row[1], row[2], row[3], row[4], row[5]]  # 1팀의 플레이어들을 가져옵니다.
                losers = [row[6], row[7], row[8], row[9], row[10]]  # 2팀의 플레이어들을 가져옵니다.
            elif winner_team == 2:
                winners = [row[6], row[7], row[8], row[9], row[10]]  # 2팀의 플레이어들을 가져옵니다.
                losers = [row[1], row[2], row[3], row[4], row[5]]  # 1팀의 플레이어들을 가져옵니다.
            
            # 이후 winners와 losers 리스트를 활용하여 원하는 작업을 수행합니다.
            await ctx.send(f'매치 시간: {match_datetime}')
            await ctx.send(f'승자 팀 플레이어들: {winners}')
            await ctx.send(f'패자 팀 플레이어들: {losers}')
    else:
        await ctx.send('등록된 경기 기록이 없습니다.')


@bot.command(name='전적')
async def recent_matches(ctx, username: str):
    # 사용자의 최근 5경기 승/패를 확인합니다.
    cursor.execute('''
        SELECT matches.match_datetime, user_matches.win_loss
        FROM user_matches
        INNER JOIN matches ON user_matches.match_id = matches.match_id
        WHERE user_matches.username = ?
        ORDER BY matches.match_datetime DESC
        LIMIT 5
    ''', (username,))
    rows = cursor.fetchall()

    if rows:
        recent_matches_info = []
        for row in rows:
            match_datetime, win_loss = row
            recent_matches_info.append(f'{match_datetime}: {"승" if win_loss == "win" else "패"}')

        # 최근 5경기 승/패 정보를 출력합니다.
        await ctx.send(f'{username}의 최근 5경기 승/패:\n' + '\n'.join(recent_matches_info))
    else:
        await ctx.send(f'{username}의 경기 기록이 없습니다.')

@bot.command(name='점수')
async def check_user_score(ctx, username: str):
    cursor.execute('''
        SELECT username, score FROM users WHERE username = ?
                   ''', (username,))
    
    row = cursor.fetchone()

    if row: await ctx.send(f'{username}의 점수는 {row[1]}입니다.')

    else: await ctx.send(f'{username} 사용자 정보는 없습니다.')




# 봇 종료 시 SQLite 연결 해제
@bot.event
async def on_disconnect():
    conn.close()

bot.run(TOKEN)

