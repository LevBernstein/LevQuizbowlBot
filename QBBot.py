import discord
from discord.ext import commands
from discord.utils import get
from time import sleep
import random as random
import operator
from collections import deque


f = open("token.txt", "r") #in token.txt, just put in your own discord api token
token = f.readline()

client = discord.Client()

class Instance:
    def __init__(self, channel):
        self.channel = channel
        self.TUnum = 0
        self.scores = {}
        self.buzzes = deque()
        self.buzzed = deque()

    def getChannel(self):
        return self.channel

    def toString(self):
        print(self.channel)
        
    def buzz(self, mem):
        if self.hasBuzzed(mem):
            print("Extra")
        else:
            self.buzzes.append(mem)
            self.buzzed.append(mem)
            print("Appended")
    
    def hasBuzzed(self, mem):
        if mem in self.buzzed:
            return True
        else:
            return False
    
    def clear(self):
        self.buzzes = deque()
        self.buzzed = deque()
    
games = [] #Array holding all active games


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name='Ready to play!'))
    print("Quizbowl Bot online!")

@client.event
async def on_message(text):
    report = ""
    text.content=text.content.lower()
    if text.content.startswith('!start'):
        current = text.channel.id
        exist = False
        for i in range(len(games)):
            if current == games[i].getChannel():
                exist = True
        if exist == False:
            report = "Starting a new game."
            x = Instance(current)
            games.append(x)
            print(x.getChannel())
            role = get(text.guild.roles, name = 'reader') #The bot needs you to make a role called "reader" in order to function.
            await text.author.add_roles(role)
        else:
            report = "You already have an active game in this channel."
        await text.channel.send(report)
           
    if text.content.startswith('!end'):
        current = text.channel.id
        exist = False
        for i in range(len(games)):
            if current == games[i].getChannel():
                exist = True
                games.pop(i)
                report = "Ended the game active in this channel."
                role = get(text.guild.roles, name = 'reader')
                await text.author.remove_roles(role)
                break
        if exist == False:
            report = "You do not currently have an active game."
        await text.channel.send(report)
    
    if text.content.startswith('buzz') or text.content.startswith('bz') or text.content.startswith('buz'):
        current = text.channel.id
        exist = False
        for i in range(len(games)):
            if current == games[i].getChannel():
                exist = True
                if games[i].hasBuzzed(text.author):
                    print(str(text.author.mention) + ", you have already buzzed.")
                else:
                    games[i].buzz(text.author)
                    print("Buzzed!")
                    report = str(text.author.mention) + " buzzed."
                    await text.channel.send(report)
                break
        if exist == False:
            report = "You need to start a game first! Use '!start' to start a game"
            await text.channel.send(report)
            
    if text.content.startswith('!clear'):#DONE
        current = text.channel.id
        exist = False
        for i in range(len(games)):
            if current == games[i].getChannel():
                exist = True
                games[i].clear()
                report = "Cleared."
        if exist == False:
            report = "You need to start a game first! Use '!start' to start a game"
        await text.channel.send(report)



client.run(token)
