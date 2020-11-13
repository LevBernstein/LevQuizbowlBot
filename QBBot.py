#Lev's Quizbowl Bot
#Author: Lev Bernstein
#Version 1.1.3


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
        self.reader = 0
        #Need an array of Member objects of each team color

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
                self.TUnum +=1
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
    
    if (text.content.startswith('!summon') or text.content.startswith('!call')) and text.author.guild_permissions.administrator:
        await text.channel.send("@everyone Time for practice!")
    
    if text.content.startswith('!team '): #Teams require the following roles: Team red, Team blue, Team green, Team orange, Team yellow, Team purple
        report = "Invalid role!"
        if text.content.startswith('!team red'):
            role = get(text.guild.roles, name = 'Team red')
            await text.author.add_roles(role)
            report = "Gave you the role, " + text.author.mention + "."
        if text.content.startswith('!team blue'):
            role = get(text.guild.roles, name = 'Team blue')
            await text.author.add_roles(role)
            report = "Gave you the role, " + text.author.mention + "."
        if text.content.startswith('!team green'):
            role = get(text.guild.roles, name = 'Team green')
            await text.author.add_roles(role)
            report = "Gave you the role, " + text.author.mention + "."
        if text.content.startswith('!team orange'):
            role = get(text.guild.roles, name = 'Team orange')
            await text.author.add_roles(role)
            report = "Gave you the role, " + text.author.mention + "."
        if text.content.startswith('!team yellow'):
            role = get(text.guild.roles, name = 'Team yellow')
            await text.author.add_roles(role)
            report = "Gave you the role, " + text.author.mention + "."
        if text.content.startswith('!team purple'):
            role = get(text.guild.roles, name = 'Team purple')
            await text.author.add_roles(role)
            report = "Gave you the role, " + text.author.mention + "."
        await text.channel.send(report)
   
    if text.content.startswith('!start'):
        current = text.channel.id
        exist = False
        for i in range(len(games)):
            if current == games[i].getChannel():
                exist = True
                break
        if exist == False:
            report = ("Starting a new game. Reader is " + text.author.mention + ".")
            x = Instance(current)
            x.reader = text.author.id
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
                if text.author.id == games[i].reader:
                    games.pop(i)
                    report = "Ended the game active in this channel."
                    role = get(text.guild.roles, name = 'reader')
                    reader = 0
                    await text.author.remove_roles(role)
                else:
                    report = "You are not the reader!"
                break
        if exist == False:
            report = "You do not currently have an active game."
        await text.channel.send(report)
            
    if text.content.startswith('!clear'):
        current = text.channel.id
        exist = False
        for i in range(len(games)):
            if current == games[i].getChannel():
                exist = True
                if text.author.id == games[i].reader:
                    games[i].clear()
                    games[i].TUnum+=1
                    report = "Cleared."
                    break
                else:
                    report = "You are not the reader!"
        if exist == False:
            report = "You need to start a game first! Use '!start' to start a game."
        await text.channel.send(report)
    
    if isInt(text.content): #Assigns points
            print(text.content + " is an int")
            current = text.channel.id
            exist = False
            for i in range(len(games)):
                if current == games[i].getChannel():
                    exist = True
                    if text.author.id == games[i].reader:
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
                emb = discord.Embed(title="Score", description="Score after TU# " + str(games[i].TUnum) + ": ", color=0x57068C)
                for x,y in games[i].scores.items():
                    if x.nick == 'none' or x.nick == 'None' or x.nick == None:
                        diction[x.name] = y
                    else:
                        diction[x.nick] = y
                sortedDict = OrderedDict(sorted(diction.items(), key = operator.itemgetter(1)))
                print(sortedDict)
                for x, y in sortedDict.items():
                    names.append(x)
                limit = len(names)
                print("Length = " + str(limit))
                #report = "Hold on a moment..." #temporary message, to be replaced with the actual scores
                #newtext = await text.channel.send(report)
                #sleep(.1)
                #report = ""
                for i in range(limit):
                    #report += (str(i+1) + ". " + names[limit-(i+1)] + ": " + str(sortedDict[names[limit-(i+1)]]) + "\r\n")
                    emb.add_field(name=(str(i+1) + ". " + names[limit-(i+1)]), value=str(sortedDict[names[limit-(i+1)]]), inline=False)
                #print(report)
                #report = "Jeff"
                #await newtext.edit(content=report) #Here, I edit the message to display the score after first displaying filler so that the bot
                #will mention users without actually pinging them.
                await text.channel.send(embed=emb)
                break
        if exist == False:
            report = "You need to start a game first! Use '!start' to start a game."
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
            report = "You need to start a game first! Use '!start' to start a game."
            await text.channel.send(report)
 
    if text.content.startswith('!github'):
        await text.channel.send("https://github.com/LevBernstein/LevQuizbowlBot")
        
    if text.content.startswith('!report'):
        await text.channel.send("https://github.com/LevBernstein/LevQuizbowlBot/issues")
 
    if text.content.startswith('!help') or text.content.startswith('!commands') or text.content.startswith('!tutorial'):
        emb = discord.Embed(title="Lev's Quizbowl Bot Commands", description="", color=0x57068C)
        emb.add_field(name= "!start", value= "Starts a new game.", inline=False)
        emb.add_field(name= "buzz", value= "Buzzes in.", inline=False)
        emb.add_field(name= "Any positive or negative whole number", value= "After a buzz, the reader can enter a whole number to assign points.", inline=False)
        emb.add_field(name= "!clear", value= "Clears buzzers after a TU goes dead.", inline=False)
        emb.add_field(name= "!score", value= "Displays the score, sorted from highest to lowest.", inline=False)
        emb.add_field(name= "!end", value= "Ends the active game.", inline=False)
        emb.add_field(name= "!team [red/blue/green/orange/yellow/purple]", value= "Assigns you the team role corresponding to the color you entered.", inline=False)
        emb.add_field(name= "!call", value= "Mentions everyone in the server and informs them that it is time for practice. Usable only by admins.", inline=False)
        emb.add_field(name= "!github", value= "Gives you a link to this bot's github page.", inline=False)
        emb.add_field(name= "!report", value= "Gives you a link to this bot's issue-reporting page.", inline=False)
        await text.channel.send(embed=emb)
        
        #await text.channel.send('Valid commands: \r\n "!start" starts a new game. \r\n "buzz" buzzes in. \r\n Enter any positive or negative whole number after someone buzzes to assign points. \r\n "!clear" clears buzzers after a TU goes dead. \r\n "!score" displays the score, sorted from highest to lowest. \r\n "!end" ends the active game. \r\n "!team [red/blue/green/orange/yellow/purple]" assigns you the team role corresponding to the color you entered. \r\n "!call" or "!summon" mentions everyone in the server and informs them it is time for practice \r\n "!github" gives you a link to this bot\'s github page. \r\n "!report" gives you a link to this bot\'s issue-reporting page. ')

client.run(token)
