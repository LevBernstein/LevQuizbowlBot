#Lev's Quizbowl Bot'
#Author: Lev Bernstein
#Version 1.0.0


import discord
from discord.ext import commands
from discord.utils import get
from time import sleep
import random as random
import operator
from collections import deque, OrderedDict


f = open("token.txt", "r") #in token.txt, just put in your own discord api token
token = f.readline()

client = discord.Client()

def isInt(st): #checks if entered message is actually the points being awarded
    if st[0] == '-' or st[0] == '+':
        return st[1:].isdigit()
    return st.isdigit()

class Instance: #instance of an active game. Every channel a game is run in gets its own instance. You cannot have more than one game per channel.
    def __init__(self, channel):
        self.channel = channel
        self.TUnum = 0
        self.scores = {}
        self.buzzes = deque()
        self.buzzed = deque()
        self.active = False

    def getChannel(self):
        return self.channel

    def toString(self):
        print(self.channel)
        
    def buzz(self, mem):
        if self.hasBuzzed(mem):
            print("Extra")
        else:
            self.active = True
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
        
    def gain(self, points):
        awarded = False
        if self.active == True:
            mem = self.buzzes.popleft()
            if points > 0:
                if mem in self.scores:
                    self.scores[mem] = self.scores[mem] + points
                    self.active = False
                    self.clear()
                    awarded = True
                else:
                    self.scores[mem] = points
                    self.active = False
                    self.clear()
                    awarded = True
            else:
                if mem in self.scores:
                    self.scores[mem] = self.scores[mem] + points
                else:
                    self.scores[mem] = points  
        return awarded
    
games = [] #Array holding all active games


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name='Ready to play!'))
    print("Quizbowl Bot online!")

@client.event
async def on_message(text):
    report = ""
    text.content=text.content.lower()
    if text.content.startswith('!start'): #DONE
        current = text.channel.id
        exist = False
        for i in range(len(games)):
            if current == games[i].getChannel():
                exist = True
                break
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
           
    if text.content.startswith('!end'): #DONE
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
    
    if text.content.startswith('buzz') or text.content.startswith('bz') or text.content.startswith('buz') or text.content.startswith('!buzz') or text.content.startswith('!bz') or text.content.startswith('!buz'):
        current = text.channel.id
        exist = False
        for i in range(len(games)):
            if current == games[i].getChannel():
                exist = True
                if games[i].hasBuzzed(text.author):
                    print(str(text.author.mention) + ", you have already buzzed.")
                else:
                    if len(games[i].buzzes) < 1:
                        games[i].buzz(text.author)
                        print("Buzzed!")
                        report = str(text.author.mention) + " buzzed."
                        await text.channel.send(report)
                    else:
                        games[i].buzz(text.author)
                        print("Buzzed!")
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
                break
        if exist == False:
            report = "You need to start a game first! Use '!start' to start a game"
        await text.channel.send(report)

    if isInt(text.content):
        print(text.content + " is an int")
        current = text.channel.id
        exist = False
        for i in range(len(games)):
            if current == games[i].getChannel():
                exist = True
                if games[i].gain(int(text.content)):
                    await text.channel.send("Awarded points. Next TU.")
                else:
                    if len(games[i].buzzes) > 0:
                        await text.channel.send((games[i].buzzes[-1]).mention + " buzzed.")
                break

    if text.content.startswith('!score'):
        names = []
        current = text.channel.id
        exist = False
        diction = {}
        for i in range(len(games)):
            if current == games[i].getChannel():
                exist = True
                for x,y in games[i].scores.items():
                    diction[x.mention] = y
                sortedDict = OrderedDict(sorted(diction.items(), key = operator.itemgetter(1)))
                print(sortedDict)
                for x, y in sortedDict.items():
                    names.append(x)
                limit = len(names)
                print("Length = " + str(limit))
                report = "Hold on a moment..."
                newtext = await text.channel.send(report)
                sleep(.1)
                report = ""
                for i in range(limit):
                    report += (str(i+1) + ". " + names[limit-(i+1)] + ": " + str(sortedDict[names[limit-(i+1)]]) + "\r\n")
                print(report)
                #report = "Jeff"
                await newtext.edit(content=report) #Here, I edit the message to display the score after first displaying filler so that the bot
                #will mention users without actually pinging them.
        if exist == False:
            report = "You need to start a game first! Use '!start' to start a game"
            await text.channel.send(report)
        
            

client.run(token)
