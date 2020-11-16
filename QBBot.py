#Lev's Quizbowl Bot
#Author: Lev Bernstein
#Version 1.3.4


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
        #TODO Need an array of Member objects of each team color
        self.bonusEnabled = True 
        self.bonusMode = False
        self.lastBonusMem = None
        self.redTeam = []
        self.blueTeam = []
        self.greenTeam = []
        self.orangeTeam = []
        self.yellowTeam = []
        self.purpleTeam = []
        self.redNeg = False
        self.blueNeg = False
        self.greenNeg = False
        self.orangeNeg = False
        self.yellowNeg = False
        self.purpleNeg = False

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
        print("Clearing...")
        self.buzzes = deque()
        self.buzzed = deque()
        self.unlock()
        
    def unlock(self):
        print("Unlocking...")
        self.redNeg = False
        self.blueNeg = False
        self.greenNeg = False
        self.orangeNeg = False
        self.yellowNeg = False
        self.purpleNeg = False
    
    def canBuzz(self, mem):
        #TODO add this to the buzz method AND to the neg part of the any integer method
        conditions = (
            (mem in self.redTeam and self.redNeg==True),
            (mem in self.blueTeam and self.blueNeg==True),
            (mem in self.greenTeam and self.greenNeg==True),
            (mem in self.orangeTeam and self.orangeNeg==True),
            (mem in self.yellowTeam and self.yellowNeg==True),
            (mem in self.purpleTeam and self.purpleNeg==True)
        )
        if any(conditions):
            return False
        else:
            return True
    
    def teamScore(self, team): #pass this one of the teams, UNTESTED. Requires further team implementation.
        #TODO test this
        sum=0
        for mem in team:
            if mem in self.scores:
                sum += self.scores[mem]
        return sum
    
    def gain(self, points):
        awarded = False
        if self.active == True:
            mem = self.buzzes.popleft()
            if points > 0: #Someone got a TU correct.
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
                self.TUnum +=1 #If a positive # of points has been assigned, that means someone got the TU correct. Advance the count.
                if self.bonusEnabled:
                    self.lastBonusMem = mem
                    self.bonusMode = True
            else: #Someone got a 0 or a -5.
                if mem in self.scores:
                    self.scores[mem] = self.scores[mem] + points
                else:
                    self.scores[mem] = points  
                if mem in self.redTeam:
                    self.redNeg = True
                    print("red locked out")
                if mem in self.blueTeam:
                    self.blueNeg = True
                    print("blue locked out")
                if mem in self.greenTeam:
                    self.greenNeg = True
                    print("green locked out")
                if mem in self.orangeTeam:
                    self.orangeNeg = True
                    print("orange locked out")
                if mem in self.yellowTeam:
                    self.yellowNeg = True
                    print("yellow locked out")
                if mem in self.purpleTeam:
                    self.purpleNeg = True
                    print("purple locked out")
        return awarded

    def bonusGain(self, points):
        if not self.bonusEnabled:
            return
        if not self.bonusMode:
            return
        self.scores[self.lastBonusMem] += points
        self.bonusMode = False
        
    def bonusStop(self):
        if self.bonusEnabled:
            self.lastBonusMem = None
            self.bonusMode = False
        else:
            return
    
games = [] #Array holding all active games


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name='Ready to play!'))
    print("Quizbowl Bot online!")

@client.event
async def on_message(text):
    report = ""
    text.content=text.content.lower()
        #print(text.content)
    if text.author.bot == False:
        if (text.content.startswith('!summon') or text.content.startswith('!call')):
            print("calling summon")
            if text.author.guild_permissions.administrator:
                await text.channel.send("@everyone Time for practice!")
            else:
                await text.channel.send("This command is only usable by server admins!")
        
        if text.content.startswith('!team '): #Teams require the following roles: Team red, Team blue, Team green, Team orange, Team yellow, Team purple
            print("calling team")
            report = "Invalid role!"
            current = text.channel.id
            exist = False
            for i in range(len(games)):
                if current == games[i].getChannel():
                    exist = True
                    break
            if exist:
                if text.content.startswith('!team r'):
                    role = get(text.guild.roles, name = 'Team red')
                    await text.author.add_roles(role)
                    report = "Gave you the role, " + text.author.mention + "."
                    games[i].redTeam.append(text.author)
                if text.content.startswith('!team b'):
                    role = get(text.guild.roles, name = 'Team blue')
                    await text.author.add_roles(role)
                    report = "Gave you the role, " + text.author.mention + "."
                    games[i].blueTeam.append(text.author)
                if text.content.startswith('!team g'):
                    role = get(text.guild.roles, name = 'Team green')
                    await text.author.add_roles(role)
                    report = "Gave you the role, " + text.author.mention + "."
                    games[i].greenTeam.append(text.author)
                if text.content.startswith('!team o'):
                    role = get(text.guild.roles, name = 'Team orange')
                    await text.author.add_roles(role)
                    report = "Gave you the role, " + text.author.mention + "."
                    games[i].orangeTeam.append(text.author)
                if text.content.startswith('!team y'):
                    role = get(text.guild.roles, name = 'Team yellow')
                    await text.author.add_roles(role)
                    report = "Gave you the role, " + text.author.mention + "."
                    games[i].yellowTeam.append(text.author)
                if text.content.startswith('!team p'):
                    role = get(text.guild.roles, name = 'Team purple')
                    await text.author.add_roles(role)
                    report = "Gave you the role, " + text.author.mention + "."
                    games[i].purpleTeam.append(text.author)
            else:
                report = "You need to start a game first! Use '!start' to start a game."
            await text.channel.send(report)
    
        if text.content.startswith('!start'):
            print("calling start")
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
                print(x.getChannel())
                role = get(text.guild.roles, name = 'reader') #The bot needs you to make a role called "reader" in order to function.
                await text.author.add_roles(role)
                games.append(x)
            else:
                report = "You already have an active game in this channel."
            await text.channel.send(report)
        
        if text.content.startswith('!end'):
            print("calling end")
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
                
        if text.content.startswith('!dead'):
            print("calling dead")
            current = text.channel.id
            exist = False
            for i in range(len(games)):
                if current == games[i].getChannel():
                    exist = True
                    if text.author.id == games[i].reader:
                        games[i].clear()
                        games[i].TUnum+=1
                        report = "TU goes dead. Next TU."
                        break
                    else:
                        report = "You are not the reader!"
            if exist == False:
                report = "You need to start a game first! Use '!start' to start a game."
            await text.channel.send(report)
        
        if text.content.startswith('!clear'):
            print("calling clear")
            current = text.channel.id
            exist = False
            for i in range(len(games)):
                if current == games[i].getChannel():
                    exist = True
                    if text.author.id == games[i].reader:
                        games[i].clear()
                        report = "Buzzers cleared, anyone can buzz."
                        break
                    else:
                        report = "You are not the reader!"
            if exist == False:
                report = "You need to start a game first! Use '!start' to start a game."
            await text.channel.send(report)
        
        if len(games) != 0 and isInt(text.content): #Assigns points. Checks if bot because, otherwise, the Bot's own embedded messages would throw errors. Checks len games to avoid unnecessary calls.
            print("calling points")
            print(text.content + " is an int")
            current = text.channel.id
            exist = False
            for i in range(len(games)):
                if current == games[i].getChannel():
                    exist = True
                    if text.author.id == games[i].reader:
                        if games[i].bonusEnabled == False: #bonuses disabled
                            if games[i].gain(int(text.content)):
                                await text.channel.send("Awarded points. Next TU.")
                            else:
                                if len(games[i].buzzes) > 0:
                                    await text.channel.send((games[i].buzzes[0]).mention + " buzzed.")
                        else: #bonuses enabled
                            if games[i].bonusMode == False:
                                if games[i].gain(int(text.content)):
                                    await text.channel.send("Awarded TU points. Awaiting bonus points.")
                                else:
                                    if len(games[i].buzzes) > 0:
                                        await text.channel.send((games[i].buzzes[0]).mention + " buzzed.")
                            else: #bonusMode true
                                games[i].bonusGain(int(text.content))
                                await text.channel.send("Awarded bonus points. Next TU.")
                    break
        
        if text.content.startswith('!bonusmode') or text.content.startswith('!btoggle'): #Toggles if bonus mode is enabled. It is enabled by default.
            print("calling bonusmode")
            current = text.channel.id
            exist = False
            for i in range(len(games)):
                if current == games[i].getChannel():
                    exist = True
                    if text.author.id == games[i].reader:
                        games[i].bonusEnabled = not games[i].bonusEnabled
                        if games[i].bonusEnabled:
                            await text.channel.send("Enabled bonus mode.")
                        else:
                            await text.channel.send("Disabled bonus mode.")
                    break
            if exist == False:
                await text.channel.send("You need to start a game first! Use '!start' to start a game.")
        
        if text.content.startswith('!bstop'): #Ends current bonus round. Use this to kill a bonus without giving points.
            print("calling bstop")
            current = text.channel.id
            exist = False
            for i in range(len(games)):
                if current == games[i].getChannel():
                    exist = True
                    if text.author.id == games[i].reader:
                        games[i].bonusStop()
                        await text.channel.send("Killed active bonus. Next TU.")
                    break
        
        if text.content.startswith('!score'):
            print("calling score")
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
                    for i in range(limit):
                        emb.add_field(name=(str(i+1) + ". " + names[limit-(i+1)]), value=str(sortedDict[names[limit-(i+1)]]), inline=False)
                    await text.channel.send(embed=emb)
                    break
            if exist == False:
                report = "You need to start a game first! Use '!start' to start a game."
                await text.channel.send(report)
    
        if text.content.startswith('buzz') or text.content.startswith('bz') or text.content.startswith('buz') or text.content.startswith('!buzz') or text.content.startswith('!bz') or text.content.startswith('!buz'):
            print("calling buzz")
            current = text.channel.id
            exist = False
            for i in range(len(games)):
                if current == games[i].getChannel():
                    exist = True
                    #This block handles all team assignment that was done before the game started.
                    red = get(text.guild.roles, name = 'Team red')
                    if red in text.author.roles and not text.author in games[i].redTeam:
                        games[i].redTeam.append(text.author)
                        print("Added " + text.author.name +  " to red on buzz")
                    blue = get(text.guild.roles, name = 'Team blue')
                    if blue in text.author.roles and not text.author in games[i].blueTeam:
                        games[i].blueTeam.append(text.author)
                        print("Added " + text.author.name +  " to blue on buzz")
                    green = get(text.guild.roles, name = 'Team green')
                    if green in text.author.roles and not text.author in games[i].greenTeam:
                        games[i].greenTeam.append(text.author)
                        print("Added " + text.author.name +  " to green on buzz")
                    orange = get(text.guild.roles, name = 'Team orange')
                    if orange in text.author.roles and not text.author in games[i].orangeTeam:
                        games[i].orangeTeam.append(text.author)
                        print("Added " + text.author.name +  " to orange on buzz")
                    yellow = get(text.guild.roles, name = 'Team yellow')
                    if yellow in text.author.roles and not text.author in games[i].yellowTeam:
                        games[i].yellowTeam.append(text.author)
                        print("Added " + text.author.name +  " to yellow on buzz")
                    purple = get(text.guild.roles, name = 'Team purple')
                    if purple in text.author.roles and not text.author in games[i].purpleTeam:
                        games[i].purpleTeam.append(text.author)
                        print("Added " + text.author.name +  " to purple on buzz")
                    
                    if games[i].bonusMode == False:
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
                    else:
                        await text.channel.send("We are currently playing a bonus. You cannot buzz.")
                    break
            if exist == False:
                report = "You need to start a game first! Use '!start' to start a game."
                await text.channel.send(report)
    
        if text.content.startswith('!github'):
            print("calling github")
            await text.channel.send("View this bot's source code at:\r\nhttps://github.com/LevBernstein/LevQuizbowlBot")
            
        if text.content.startswith('!report'):
            print("calling report")
            await text.channel.send("Report any issues at:\r\nhttps://github.com/LevBernstein/LevQuizbowlBot/issues")
    
        if text.content.startswith('!help') or text.content.startswith('!commands') or text.content.startswith('!tutorial'):
            print("calling tutorial")
            emb = discord.Embed(title="Lev's Quizbowl Bot Commands", description="", color=0x57068C)
            emb.add_field(name= "!start", value= "Starts a new game.", inline=True)
            emb.add_field(name= "buzz", value= "Buzzes in.", inline=True)
            emb.add_field(name= "!end", value= "Ends the active game.", inline=True)
            emb.add_field(name= "!clear", value= "Clears buzzes without advancing the TU count.", inline=True)
            emb.add_field(name= "!dead", value= "Clears buzzes after a dead TU and advances the TU count.", inline=True)
            emb.add_field(name= "!score", value= "Displays the score, sorted from highest to lowest.", inline=True)
            emb.add_field(name= "Any whole number", value= "After a buzz or a bonus, the reader can enter a +/- whole number to assign points.", inline=True)
            emb.add_field(name= "!team [r/b/g/o/y/p]", value= "Assigns you the team role corresponding to the color you entered.", inline=True)
            emb.add_field(name= "!call", value= "Mentions everyone in the server and informs them that it is time for practice. Usable only by admins.", inline=True)
            emb.add_field(name= "!github", value= "Gives you a link to this bot's github page.", inline=True)
            emb.add_field(name= "!report", value= "Gives you a link to this bot's issue-reporting page.", inline=True)
            emb.add_field(name= "!tu", value= "Reports the current tossup number.", inline=True)
            emb.add_field(name= "!bonusmode", value= "Disables or enables. Bonuses are enabled by default.", inline=True)
            emb.add_field(name= "!bstop", value= "Kills an active bonus without giving points.", inline=True)
            emb.add_field(name= "!tutorial", value= "Shows you this list.", inline=True)
            await text.channel.send(embed=emb)
            
            #await text.channel.send('Valid commands: \r\n "!start" starts a new game. \r\n "buzz" buzzes in. \r\n Enter any positive or negative whole number after someone buzzes to assign points. \r\n "!clear" clears buzzers after a TU goes dead. \r\n "!score" displays the score, sorted from highest to lowest. \r\n "!end" ends the active game. \r\n "!team [red/blue/green/orange/yellow/purple]" assigns you the team role corresponding to the color you entered. \r\n "!call" or "!summon" mentions everyone in the server and informs them it is time for practice \r\n "!github" gives you a link to this bot\'s github page. \r\n "!report" gives you a link to this bot\'s issue-reporting page. ')

        elif text.content.startswith('!tu'): #elif not if because otherwise !tutorial calls this too
            print("calling tu")
            current = text.channel.id
            exist = False
            for i in range(len(games)):
                if current == games[i].getChannel():
                    exist = True
                    report = "Current TU: #" + str(games[i].TUnum + 1) + "."
            if exist == False:
                report = "You need to start a game first! Use '!start' to start a game."
            await text.channel.send(report)

client.run(token)
