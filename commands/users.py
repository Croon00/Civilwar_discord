import discord
from discord.ext import commands
from database.db import get_db_connection

def setup(bot):
    conn, cursor = get_db_connection()

    @bot.command(name='사용자추가')
    async def add_info(ctx, username: str, score: int):
        cursor.execute('INSERT OR REPLACE INTO users (username, score) VALUES (?, ?)', (username, score))
        conn.commit()
        await ctx.send(f'사용자 정보를 추가했습니다: {username}, {score}')
    
    @bot.command(name='모든사용자')
    async def all_user_info(ctx):
        all_info = []
        cursor.execute('SELECT * FROM users ORDER BY score DESC')
        rows = cursor.fetchall()
        for row in rows:
            user_info_str = f'{row[0]} : {row[1]}, Top : {row[2]} Low : {row[3]}'
            all_info.append(user_info_str)

        if all_info:
            await ctx.send('\n'.join(all_info))
        else:
            await ctx.send('등록된 사용자 정보가 없습니다.')
    
    @bot.command(name='점수수정')
    async def modify_info(ctx, username: str, score: int):
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        if row:
            cursor.execute('UPDATE users SET score = ? WHERE username = ?', (score, username,))
            conn.commit()
            await ctx.send(f'{username}의 정보가 수정되었습니다.')
        else:
            await ctx.send(f'{username}은(는) 등록되지 않은 사용자입니다.')

    @bot.command(name='점수')
    async def check_user_score(ctx, username: str):
        cursor.execute('SELECT username, score FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        if row:
            await ctx.send(f'{username}의 점수는 {row[1]}입니다.')
        else:
            await ctx.send(f'{username} 사용자 정보는 없습니다.')
