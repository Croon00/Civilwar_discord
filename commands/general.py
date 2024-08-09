import discord
from discord.ext import commands
from database.db import get_db_connection

def setup(bot):
    @bot.command(name="명령어")
    async def my_help(ctx):
        embed = discord.Embed(title="Custom Help", description="명령어들:")
        embed.add_field(name="사용자추가", value="(이름, 점수)을 통해 사용자 추가")
        embed.add_field(name="모든사용자", value="모든 사용자 점수 정보 확인")
        embed.add_field(name="전적", value="(이름)을 통해 최근 5경기 전적 확인")
        embed.add_field(name="점수", value="(이름)을 통해 현재 점수 확인 ")
        embed.add_field(name="점수수정", value="(이름, 점수)를 통해 해당 사람 점수 수정")
        embed.add_field(name="최근매치", value="가장 최근 시간으로 5 경기 매치 결과 확인")
        embed.add_field(name="팀나누기", value="(이름 * 10)을 통해 5대 5로 최소한의 점수로 팀 나누기")
        embed.add_field(name="팀1승리", value="가장 최근 나눈 팀을 기준으로 1팀 승리 ")
        embed.add_field(name="팀2승리", value="가장 최근 나눈 팀을 기준으로 2팀 승리 ")
        embed.add_field(name="같은팀승률", value="(이름 2 ~ 5명)을 통해 해당 사람들이 같은팀일 경우 승률 확인")
        embed.add_field(name="상대승률", value="(이름, 이름)을 통해 해당 사람들이 상대팀일 경우 승률 확인")
        embed.add_field(name="개인승률", value="(이름)을 통해 해당 사람의 여태까지의 승률 확인")
        embed.add_field(name="시즌1 정보들", value="(상대승률, 개인승률, 같은팀승률, 모든사용자) 앞에 '시즌1'붙여 쓰면 시즌1 정보 확인 가능")
        embed.add_field(name="챔피언", value="(챔피언) 을 통해서 해당 챔피언의 기본 스탯 확인 가능")
        embed.add_field(name="숙련도", value="(이름)을 통해서 해당 사람의 챔피언 숙련도 top 5 정보 확인 가능")
        embed.add_field(name="mvp", value="(이름)을 통해서 mvp 투표")
        embed.add_field(name="mvp비우기", value="mvp 투표했던거 초기화")
        await ctx.send(embed=embed)
