import discord
from discord.ext import commands
import itertools
import random
from datetime import datetime
import pytz
from database.db import get_db_connection

def setup(bot):
    conn, cursor = get_db_connection()
    
    # 모든 사용자 정보 (시즌 1)
    @bot.command(name='시즌1모든사용자')
    async def all_user_info_season1(ctx):
        all_info = []
        cursor.execute('SELECT * FROM users_season1 ORDER BY score DESC')
        rows = cursor.fetchall()
        
        if rows:
            embed = discord.Embed(title="시즌 1 모든 사용자 정보", description="시즌 1 사용자의 점수 정보를 확인하세요", color=0x00ff00)
            for i, row in enumerate(rows):
                username = row[0]
                score = row[1]
                top_score = row[2]
                low_score = row[3]
                user_info_str = f"점수: {score}, Top: {top_score}, Low: {low_score}"
                embed.add_field(name=username, value=user_info_str, inline=True)
                
                # 3명씩 묶어서 한 줄에 보여주기 위해 newline 추가
                if (i + 1) % 3 == 0:
                    embed.add_field(name='\u200b', value='\u200b', inline=False)
                    
            await ctx.send(embed=embed)
        else:
            await ctx.send('등록된 사용자 정보가 없습니다.')


    # 같은 팀 승률 계산 (시즌 1)
    @bot.command(name='시즌1같은팀승률')
    async def calculate_same_team_win_rate_season1(ctx, *usernames):
        if len(usernames) < 2 or len(usernames) > 5:
            await ctx.send('2명에서 5명의 사용자 이름을 입력해주세요.')
            return

        user_matches = {username: {} for username in usernames}

        for username in usernames:
            cursor.execute('''
                SELECT match_id, win_loss
                FROM user_matches_season1
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

        embed = discord.Embed(title="시즌 1 같은 팀 승률", description=result_message, color=0x00ff00)
        await ctx.send(embed=embed)

    # 상대 승률 계산 (시즌 1)
    @bot.command(name='시즌1상대승률')
    async def calculate_opponent_win_rate_season1(ctx, username1, username2):
        user_matches = {username: {} for username in [username1, username2]}

        for username in [username1, username2]:
            cursor.execute('''
                SELECT match_id, win_loss
                FROM user_matches_season1
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

        embed = discord.Embed(title="시즌 1 상대 승률", description=result_message, color=0x00ff00)
        await ctx.send(embed=embed)

    # 개인 승률 계산 (시즌 1)
    @bot.command(name='시즌1개인승률')
    async def calculate_individual_win_rate_season1(ctx, username):
        cursor.execute("SELECT COUNT(*) FROM user_matches_season1 WHERE username = ? AND win_loss = 'win'", (username,))
        wins = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM user_matches_season1 WHERE username = ? AND win_loss = 'loss'", (username,))
        losses = cursor.fetchone()[0]
        total_matches = wins + losses

        if total_matches == 0:
            win_rate = 0
            result_message = f'{username}님은 아직 한 경기도 안했습니다.'
        else:
            win_rate = (wins / total_matches) * 100
            result_message = f'{username}님의 개인 승률: {win_rate:.2f}%, 총 판수 : {total_matches}, 이긴 판수 : {wins}'

        embed = discord.Embed(title="시즌 1 개인 승률", description=result_message, color=0x00ff00)
        await ctx.send(embed=embed)
