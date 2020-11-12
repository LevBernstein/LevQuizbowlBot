import discord
from discord.ext import commands
from discord.utils import get
from time import sleep
import random as random
import operator


f = open("token.txt", "r") #in token.txt, just put in your own discord api token
token = f.readline()

client = discord.Client()

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name='Ready to play!'))
    print("Quizbowl Bot online!")

@client.event
async def on_message(text):
    report = ""
    text.content=text.content.lower()
    if text.content.startswith('!start'):
            report = "Starting a new game."
            await text.channel.send(report)
             
             
client.run(token)
