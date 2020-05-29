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


async def send_dm(**kwargs):
    member = kwargs.get("member")
    payload = kwargs.get("payload")
    dm_channel = await member.create_dm()
    if member.nick not in DM_RECIPIENTS:
        message = payload.get(member.nick)
        DM_RECIPIENTS.append(member.nick)
    else:
        message = random.choice(payload.get("random"))
    await dm_channel.send(message)


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
        await send_channel(member=message.author, payload=response["payload"],
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
