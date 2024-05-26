import discord
from discord.ext import commands
import itertools
import random
from datetime import datetime
import pytz
from database.db import get_db_connection

def setup(bot):
    conn, cursor = get_db_connection()
    
    mvp_list = {}
    team1_scores = {}
    team2_scores = {}

    def get_streak(cursor, username):
        cursor.execute('''
            SELECT win_loss 
            FROM user_matches 
            WHERE username = ? 
            ORDER BY match_datetime DESC 
            LIMIT 2
        ''', (username,))
        rows = cursor.fetchall()
        if len(rows) == 2 and rows[0][0] == rows[1][0]:
            return rows[0][0]
        return None

    @bot.command(name='팀나누기')
    async def random_team_split(ctx, *users):
        nonlocal team1_scores, team2_scores
        
        if len(users) != 10:
            await ctx.send('10명의 사용자 이름을 입력해주세요.')
            return

        user_scores = {}
        for username in users:
            cursor.execute('SELECT score FROM users WHERE username = ?', (username,))
            row = cursor.fetchone()
            if row:
                user_scores[username] = row[0]
            else:
                await ctx.send(f'{username}의 점수를 찾을 수 없습니다.')
                return

        all_team_compositions = list(itertools.combinations(user_scores.items(), len(users) // 2))
        min_score_diff = float('inf')
        best_team_compositions = []
        for team_composition in all_team_compositions:
            team1 = team_composition
            team2 = [(username, score) for username, score in user_scores.items() if (username, score) not in team_composition]
            team1_score = sum(score for _, score in team1)
            team2_score = sum(score for _, score in team2)
            score_diff = abs(team1_score - team2_score)
            if score_diff < min_score_diff:
                min_score_diff = score_diff
                best_team_compositions = [(team1, team2)]
            elif score_diff == min_score_diff:
                best_team_compositions.append((team1, team2))

        chosen_team_composition = random.choice(best_team_compositions)
        team1, team2 = chosen_team_composition
        team1_score = sum(score for _, score in team1)
        team2_score = sum(score for _, score in team2)
        
        team1_scores = dict(team1)
        team2_scores = dict(team2)

        team1_sorted = sorted(team1, key=lambda x: x[1])
        team2_sorted = sorted(team2, key=lambda x: x[1])

        # 팀 구성원을 한 줄로 나열
        team1_members = ", ".join([f"{user[0]}: {user[1]}" for user in team1_sorted])
        team2_members = ", ".join([f"{user[0]}: {user[1]}" for user in team2_sorted])

        embed = discord.Embed(title="팀 나누기 결과", description=f"Score Difference: {min_score_diff}", color=0x00ff00)
        embed.add_field(name="Team 1", value=team1_members, inline=False)
        embed.add_field(name="Team 1 Score", value=str(team1_score), inline=False)
        embed.add_field(name="Team 2", value=team2_members, inline=False)
        embed.add_field(name="Team 2 Score", value=str(team2_score), inline=False)

        await ctx.send(embed=embed)

    @bot.command(name='팀1승리')
    async def team1_win(ctx):
        nonlocal team1_scores, team2_scores
        if len(team1_scores) == 0:
            await ctx.send("팀부터 나눠라")
            return
        
        korea_timezone = pytz.timezone('Asia/Seoul')
        korea_now = datetime.now(tz=korea_timezone)
        match_end_time = korea_now.strftime('%Y-%m-%d %H:%M:%S')
        winner_team = 1

        for username, score in team1_scores.items():
            streak = get_streak(cursor, username)
            points_to_add = 1
            if streak == 'win':
                points_to_add = 2
            cursor.execute('UPDATE users SET score = score + ? WHERE username = ?', (points_to_add, username))
            cursor.execute('UPDATE users SET top_score = MAX(score, top_score) WHERE username = ?', (username,))
            cursor.execute('UPDATE users SET low_score = MIN(score, low_score) WHERE username = ?', (username,))
        for username, score in team2_scores.items():
            streak = get_streak(cursor, username)
            points_to_subtract = 1
            if streak == 'loss':
                points_to_subtract = 2
            cursor.execute('UPDATE users SET score = score - ? WHERE username = ?', (points_to_subtract, username))
            cursor.execute('UPDATE users SET top_score = MAX(score, top_score) WHERE username = ?', (username,))
            cursor.execute('UPDATE users SET low_score = MIN(score, low_score) WHERE username = ?', (username,))
        conn.commit()

        cursor.execute('INSERT INTO matches (team1_username1, team1_username2, team1_username3, team1_username4, team1_username5, '
                       'team2_username1, team2_username2, team2_username3, team2_username4, team2_username5, '
                       'winner_team, match_datetime) '
                       'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                       (*team1_scores.keys(), *team2_scores.keys(), winner_team, match_end_time))
        conn.commit()

        match_id = cursor.lastrowid
        for username, score in team1_scores.items():
            cursor.execute('INSERT INTO user_matches (username, match_id, win_loss, match_datetime) VALUES (?, ?, ?, ?)', 
                           (username, match_id, 'win', match_end_time))
        for username, score in team2_scores.items():
            cursor.execute('INSERT INTO user_matches (username, match_id, win_loss, match_datetime) VALUES (?, ?, ?, ?)', 
                           (username, match_id, 'loss', match_end_time))

        conn.commit()

        team1_scores = {}
        team2_scores = {}
        
        embed = discord.Embed(title="팀 1 승리", description="팀 1이 승리했습니다!", color=0x00ff00)
        await ctx.send(embed=embed)

    @bot.command(name='팀2승리')
    async def team2_win(ctx):
        nonlocal team1_scores, team2_scores
        if len(team1_scores) == 0:
            await ctx.send("팀부터 나눠라")
            return
        
        korea_timezone = pytz.timezone('Asia/Seoul')
        korea_now = datetime.now(tz=korea_timezone)
        match_end_time = korea_now.strftime('%Y-%m-%d %H:%M:%S')
        winner_team = 2

        for username, score in team1_scores.items():
            streak = get_streak(cursor, username)
            points_to_subtract = 1
            if streak == 'loss':
                points_to_subtract = 2
            cursor.execute('UPDATE users SET score = score - ? WHERE username = ?', (points_to_subtract, username))
            cursor.execute('UPDATE users SET top_score = MAX(score, top_score) WHERE username = ?', (username,))
            cursor.execute('UPDATE users SET low_score = MIN(score, low_score) WHERE username = ?', (username,))
        for username, score in team2_scores.items():
            streak = get_streak(cursor, username)
            points_to_add = 1
            if streak == 'win':
                points_to_add = 2
            cursor.execute('UPDATE users SET score = score + ? WHERE username = ?', (points_to_add, username))
            cursor.execute('UPDATE users SET top_score = MAX(score, top_score) WHERE username = ?', (username,))
            cursor.execute('UPDATE users SET low_score = MIN(score, low_score) WHERE username = ?', (username,))
        conn.commit()

        cursor.execute('INSERT INTO matches (team1_username1, team1_username2, team1_username3, team1_username4, team1_username5, '
                       'team2_username1, team2_username2, team2_username3, team2_username4, team2_username5, '
                       'winner_team, match_datetime) '
                       'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                       (*team1_scores.keys(), *team2_scores.keys(), winner_team, match_end_time))
        conn.commit()

        match_id = cursor.lastrowid
        for username, score in team1_scores.items():
            cursor.execute('INSERT INTO user_matches (username, match_id, win_loss, match_datetime) VALUES (?, ?, ?, ?)', 
                           (username, match_id, 'loss', match_end_time))
        for username, score in team2_scores.items():
            cursor.execute('INSERT INTO user_matches (username, match_id, win_loss, match_datetime) VALUES (?, ?, ?, ?)', 
                           (username, match_id, 'win', match_end_time))

        conn.commit()

        team1_scores = {}
        team2_scores = {}
        
        embed = discord.Embed(title="팀 2 승리", description="팀 2가 승리했습니다!", color=0x00ff00)
        await ctx.send(embed=embed)
 # 같은 팀 승률 계산
    @bot.command(name='같은팀승률')
    async def calculate_same_team_win_rate(ctx, *usernames):
        if len(usernames) < 2 or len(usernames) > 5:
            await ctx.send('2명에서 5명의 사용자 이름을 입력해주세요.')
            return

        user_matches = {username: {} for username in usernames}

        for username in usernames:
            cursor.execute('''
                SELECT match_id, win_loss
                FROM user_matches
                WHERE username = ?
            ''', (username,))
            rows = cursor.fetchall()
            for match_id, win_loss in rows:
                user_matches[username][match_id] = win_loss

        total_same_team = 0
        total_same_team_win = 0

        for match_id in set.intersection(*(set(matches.keys()) for matches in user_matches.values())):
            same_team_win = all(user_matches[username][match_id] == 'win' for username in usernames)
            same_team_loss = all(user_matches[username][match_id] == 'loss' for username in usernames)

            if same_team_win:
                total_same_team_win += 1
            if same_team_win or same_team_loss:
                total_same_team += 1

        if total_same_team > 0:
            win_rate = (total_same_team_win / total_same_team) * 100
            usernames_str = ', '.join(usernames)
            result_message = f'({usernames_str}) 같은 팀일 때 승률: {win_rate:.2f}%, 총 판수: {total_same_team}판'
        else:
            result_message = '같은 팀이었던 경우가 없습니다.'

        embed = discord.Embed(title="같은 팀 승률", description=result_message, color=0x00ff00)
        await ctx.send(embed=embed)

    # 상대 승률 계산
    @bot.command(name='상대승률')
    async def calculate_opponent_win_rate(ctx, username1, username2):
        user_matches = {username: {} for username in [username1, username2]}

        for username in [username1, username2]:
            cursor.execute('''
                SELECT match_id, win_loss
                FROM user_matches
                WHERE username = ?
            ''', (username,))
            rows = cursor.fetchall()
            for match_id, win_loss in rows:
                user_matches[username][match_id] = win_loss

        total_opponent_games = {username: set() for username in [username1, username2]}
        total_opponent_win = {username: 0 for username in [username1, username2]}

        for match_id in set.intersection(set(user_matches[username1].keys()), set(user_matches[username2].keys())):
            if user_matches[username1][match_id] == 'win' and user_matches[username2][match_id] == 'loss':
                total_opponent_games[username2].add(match_id)
                total_opponent_win[username1] += 1
            elif user_matches[username1][match_id] == 'loss' and user_matches[username2][match_id] == 'win':
                total_opponent_games[username1].add(match_id)
                total_opponent_win[username2] += 1

        total_opponent_games_combined = len(total_opponent_games[username1] | total_opponent_games[username2])

        opponent_win_rates = {}
        for username in [username1, username2]:
            if total_opponent_games_combined > 0:
                opponent_win_rates[username] = (total_opponent_win[username] / total_opponent_games_combined) * 100
            else:
                await ctx.send('서로 상대한 적이 없습니다.')
                return

        result_message = f'{username1} vs {username2}\n'
        for username in [username1, username2]:
            result_message += f'{username}의 상대승률: {opponent_win_rates[username]:.2f}%, 총 판수 : {total_opponent_games_combined}, 이긴 판수 : {total_opponent_win[username]}\n'

        embed = discord.Embed(title="상대 승률", description=result_message, color=0x00ff00)
        await ctx.send(embed=embed)

    # 개인 승률 계산
    @bot.command(name='개인승률')
    async def calculate_individual_win_rate(ctx, username):
        cursor.execute("SELECT COUNT(*) FROM user_matches WHERE username = ? AND win_loss = 'win'", (username,))
        wins = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM user_matches WHERE username = ? AND win_loss = 'loss'", (username,))
        losses = cursor.fetchone()[0]
        total_matches = wins + losses

        if total_matches == 0:
            win_rate = 0
            result_message = f'{username}님은 아직 한 경기도 안했습니다.'
        else:
            win_rate = (wins / total_matches) * 100
            result_message = f'{username}님의 개인 승률: {win_rate:.2f}%, 총 판수 : {total_matches}, 이긴 판수 : {wins}'

        embed = discord.Embed(title="개인 승률", description=result_message, color=0x00ff00)
        await ctx.send(embed=embed)


    @bot.command(name='mvp')
    async def add_mvp(ctx, username: str):
        nonlocal mvp_list
        cursor.execute('SELECT score FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        
        if row:
            # Increment the vote count for the user
            if username in mvp_list:
                mvp_list[username]['votes'] += 1
            else:
                mvp_list[username] = {'score': row[0], 'votes': 1}
            
            await ctx.send(f'{username}가 MVP 후보로 추가되었습니다. 현재 투표 수: {mvp_list[username]["votes"]}')
        else:
            await ctx.send(f'{username}를 찾을 수 없습니다.')

        # Check if the total votes reach 10
        total_votes = sum(user['votes'] for user in mvp_list.values())
        if total_votes >= 10:
            # Find the maximum score among the users
            max_score = max(user['score'] for user in mvp_list.values())
            top_users = [user for user, data in mvp_list.items() if data['score'] == max_score]

            for user in top_users:
                cursor.execute('UPDATE users SET mvp_point = mvp_point + 100 WHERE username = ?', (user,))
            conn.commit()

            await ctx.send(f'MVP 포인트가 추가되었습니다: {", ".join(top_users)}')

            # Reset the mvp_list after processing
            mvp_list = {}
    
    @bot.command(name='mvp비우기')
    async def clear_mvp_list(ctx):
        nonlocal mvp_list
        mvp_list = {}
        await ctx.send('MVP 후보 리스트가 초기화되었습니다.')
