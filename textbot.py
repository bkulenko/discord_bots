import json
import os
import random

import discord
from dotenv import load_dotenv

load_dotenv()
token = os.environ.get("DISCORD_TOKEN")
GUILD = os.environ.get("DISCORD_GUILD")

client = discord.Client()


DM_RECIPIENTS = []
LOTTERY = []


async def send_dm(**kwargs):
    member = kwargs.get("member")
    payload = kwargs.get("payload")
    dm_channel = await member.create_dm()
    message = payload.get(member.nick)
    await dm_channel.send(message)


async def lottery_add(**kwargs):
    member = kwargs.get("member")
    if member.nick not in LOTTERY:
        LOTTERY.append(member.nick)


async def lottery_call(**kwargs):
    winner = random.choice(LOTTERY)
    channel = kwargs.get("channel")
    payload = kwargs.get("payload")
    guild = discord.utils.get(client.guilds, name=GUILD)
    member = discord.utils.get(guild.members, nick=winner)
    channel = discord.utils.get(guild.channels, name=channel)
    await channel.send(payload.format(member.mention))


async def send_channel(**kwargs):
    member = kwargs.get("member")
    payload = kwargs.get("payload")
    channel = kwargs.get("channel")
    guild = discord.utils.get(client.guilds, name=GUILD)
    channel = discord.utils.get(guild.channels, name=channel)
    if isinstance(payload, dict) and payload.get(member.nick):
        message = payload.get(member.nick)
    else:
        message = random.choice(payload)
    await channel.send(message.format(member.mention))


with open("config.json") as config:
    message_mapping = json.load(config)


@client.event
async def on_ready():
    print(f"{client.user} has connected to Discord!")
    guild = discord.utils.get(client.guilds, name=GUILD)
    members = "\n".join([member.name for member in guild.members])
    print(members)


@client.event
async def on_message(message):
    print(DM_RECIPIENTS)
    commands = message_mapping.get("commands")
    response = commands.get(message.content)
    if response:
        func = response.get("function")
        if not func:
            await send_channel(member=message.author, payload=response["payload"],
                               channel=response["channel"])
        else:
            func = globals().get(func)
            await func(member=message.author, payload=response["payload"],
                       channel=response["channel"])


@client.event
async def on_voice_state_update(member, before, after):
    if (not before.channel or before.channel != after.channel) and after.channel:
        channel_name = after.channel.name
        func = message_mapping.get(channel_name)
        if func:
            call = globals().get(func["function"])
            await call(member=member, payload=func["payload"], channel=func.get("channel"))


client.run(token)
