import discord
from discord.ext import commands
import requests
import json
from datetime import datetime
from database.db import get_db_connection

def setup(bot):
    conn, cursor = get_db_connection()

    # Load Riot API key from config file
    with open('config.json') as config_file:
        config = json.load(config_file)
    RIOT_API_KEY = config['Riot_API_Key']

    # Load champion data from champion.json
    with open('champion.json', encoding='utf-8') as champion_file:
        champion_data = json.load(champion_file)['data']
    
    champion_id_to_name = {int(details['key']): details['name'] for _, details in champion_data.items()}
    name_to_champion = {details['name']: details for _, details in champion_data.items()}

    @bot.command(name='숙련도')
    async def champion_mastery(ctx, username: str):
        # Get the PUUID for the given username
        cursor.execute('SELECT lol_puuid FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        if row:
            puuid = row[0]
        else:
            await ctx.send(f'{username}의 PUUID를 찾을 수 없습니다.')
            return

        # Make the API request to Riot Games
        url = f'https://kr.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/top'
        headers = {
            'X-Riot-Token': RIOT_API_KEY
        }
        params = {
            'count': 5
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            await ctx.send('챔피언 숙련도 정보를 가져오는 데 실패했습니다.')
            return

        # Parse the response
        mastery_data = response.json()

        # Create an embed message
        embed = discord.Embed(title=f"{username}의 챔피언 숙련도", description="상위 5개의 챔피언 숙련도 정보입니다.", color=0x00ff00)
        for champion in mastery_data:
            champion_id = champion['championId']
            champion_name = champion_id_to_name.get(champion_id, "Unknown")
            last_play_time = datetime.utcfromtimestamp(champion['lastPlayTime'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
            champion_level = champion['championLevel']
            champion_points = champion['championPoints']
            embed.add_field(name=f"챔피언: {champion_name}", 
                            value=f"마지막 플레이 시간: {last_play_time}\n레벨: {champion_level}\n포인트: {champion_points}", 
                            inline=False)

        await ctx.send(embed=embed)

    
    @bot.command(name='챔피언')
    async def champion_info(ctx, champion_name: str):
        champion_info = name_to_champion.get(champion_name)
        if not champion_info:
            await ctx.send(f'{champion_name} 챔피언을 찾을 수 없습니다.')
            return

        stats = champion_info.get('stats', {})
        hp = stats.get('hp', '정보 없음')
        hp_per_level = stats.get('hpperlevel', '정보 없음')
        mp = stats.get('mp', '정보 없음')
        mp_per_level = stats.get('mpperlevel', '정보 없음')
        movespeed = stats.get('movespeed', '정보 없음')
        armor = stats.get('armor', '정보 없음')
        armor_per_level = stats.get('armorperlevel', '정보 없음')
        spellblock = stats.get('spellblock', '정보 없음')
        spellblock_per_level = stats.get('spellblockperlevel', '정보 없음')
        attack_range = stats.get('attackrange', '정보 없음')
        hp_regen = stats.get('hpregen', '정보 없음')
        hp_regen_per_level = stats.get('hpregenperlevel', '정보 없음')
        mp_regen = stats.get('mpregen', '정보 없음')
        mp_regen_per_level = stats.get('mpregenperlevel', '정보 없음')
        attack_damage = stats.get('attackdamage', '정보 없음')
        attack_damage_per_level = stats.get('attackdamageperlevel', '정보 없음')
        attack_speed_per_level = stats.get('attackspeedperlevel', '정보 없음')
        attack_speed = stats.get('attackspeed', '정보 없음')

        fields = [
            ("기본 체력", str(hp)),
            ("레벨당 체력 증가", str(hp_per_level)),
            ("기본 마나", str(mp)),
            ("레벨당 마나 증가", str(mp_per_level)),
            ("이동 속도", str(movespeed)),
            ("기본 방어력", str(armor)),
            ("레벨당 방어력 증가", str(armor_per_level)),
            ("기본 마법 저항력", str(spellblock)),
            ("레벨당 마법 저항력 증가", str(spellblock_per_level)),
            ("공격 거리", str(attack_range)),
            ("기본 체력 재생", str(hp_regen)),
            ("레벨당 체력 재생 증가", str(hp_regen_per_level)),
            ("기본 마나 재생", str(mp_regen)),
            ("레벨당 마나 재생 증가", str(mp_regen_per_level)),
            ("기본 공격력", str(attack_damage)),
            ("레벨당 공격력 증가", str(attack_damage_per_level)),
            ("레벨당 공격 속도 증가", str(attack_speed_per_level)),
            ("기본 공격 속도", str(attack_speed))
        ]

        embeds = []
        embed = discord.Embed(title=f"{champion_name} 정보", color=0x00ff00)
        
        for i, (name, value) in enumerate(fields):
            embed.add_field(name=name, value=value, inline=True)
            if (i + 1) % 3 == 0:
                embed.add_field(name='\u200b', value='\u200b', inline=False)
            if len(embed.fields) >= 25:
                embeds.append(embed)
                embed = discord.Embed(color=0x00ff00)
        
        if len(embed.fields) > 0:
            embeds.append(embed)
        
        for embed in embeds:
            await ctx.send(embed=embed)
