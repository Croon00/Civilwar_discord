import discord
from discord.ext import commands
from database.db import get_db_connection

def setup(bot):
    conn, cursor = get_db_connection()

    @bot.command(name='사용자추가')
    async def add_info(ctx, username: str, score: int):
        cursor.execute('INSERT OR REPLACE INTO users (username, score) VALUES (?, ?)', (username, score))
        conn.commit()
        embed = discord.Embed(title="사용자 추가", description=f'사용자 정보를 추가했습니다: {username}, {score}', color=0x00ff00)
        await ctx.send(embed=embed)
    
    @bot.command(name='모든사용자')
    async def all_user_info(ctx):
        cursor.execute('SELECT * FROM users ORDER BY score DESC')
        rows = cursor.fetchall()
        
        if rows:
            embed = discord.Embed(title="모든 사용자 정보", description="사용자의 점수 정보를 확인하세요", color=0x00ff00)
            for i, row in enumerate(rows):
                username = row[0]
                score = row[1]
                top_score = row[2]
                low_score = row[3]
                mvp_point = row[5]
                user_info_str = f"점수: {score}, Top: {top_score}, Low: {low_score}, MVP_POINT : {mvp_point}"
                embed.add_field(name=username, value=user_info_str, inline=True)
                
                # 3명씩 묶어서 한 줄에 보여주기 위해 newline 추가
                if (i + 1) % 3 == 0:
                    embed.add_field(name='\u200b', value='\u200b', inline=False)
                    
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="모든 사용자 정보", description="등록된 사용자 정보가 없습니다.", color=0xff0000)
            await ctx.send(embed=embed)
    
    @bot.command(name='점수수정')
    async def modify_info(ctx, username: str, score: int):
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        if row:
            cursor.execute('UPDATE users SET score = ? WHERE username = ?', (score, username,))
            conn.commit()
            embed = discord.Embed(title="점수 수정", description=f'{username}의 정보가 수정되었습니다.', color=0x00ff00)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="점수 수정", description=f'{username}은(는) 등록되지 않은 사용자입니다.', color=0xff0000)
            await ctx.send(embed=embed)

    @bot.command(name='점수')
    async def check_user_score(ctx, username: str):
        cursor.execute('SELECT username, score FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        if row:
            embed = discord.Embed(title="점수 확인", description=f'{username}의 점수는 {row[1]}입니다.', color=0x00ff00)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="점수 확인", description=f'{username} 사용자 정보는 없습니다.', color=0xff0000)
            await ctx.send(embed=embed)