# Lev's Quizbowl Bot
# Author: Lev Bernstein
# Version: 1.4.8
# This bot is designed to be a user-friendly Quizbowl Discord bot with a minimum of setup.
# All commands are documented; if you need any help understanding them, try the command !tutorial.


from time import sleep
from datetime import datetime
import random as random
import operator
from collections import deque, OrderedDict

import discord
from discord.ext import commands
from discord.utils import get

f = open("token.txt", "r") # in token.txt, just put in your own discord api token
token = f.readline()

client = discord.Client()

def isInt(st):
    """Checks if an entered string would be a valid number of points to assign."""
    if st.startswith('<:neg:') or st.startswith('<:ten:') or st.startswith('<:power:'):
        return True
    if st[0] == '-' or st[0] == '+':
        return st[1:].isdigit()
    return st.isdigit()

def isBuzz(st):
    """Checks if an entered string is a valid buzz."""
    if st.startswith('buzz') or st.startswith('bz') or st.startswith('buz') or st.startswith('!buzz') or st.startswith('!bz') or st.startswith('!buz') or st.startswith(':bee:') or st.startswith('<:buzz:'):
        return True
    return False

#############################################################
# Instance(self, channel)
# This class is an instance of an active game of Quizbowl.
# Every channel in which a game is run gets its own instance.
# You cannot have more than one Instance per channel.
# Parameters: channel is the id of the Discord channel in which the instance is run.
# Local variables:
#   Tunum: Represents the number of completed TUs read. Advances after points are awarded for a TU or a TU goes dead (!dead).
#   scores: Dictionary mapping players to the number of points they have.
#   buzzes: Queue containing players' buzzes. After a player negs, they are popped from the queue and it moves on to the next buzz.
#   buzzed: Queue containing players who have already buzzed. If a player is in this queue, they cannot buzz again. You can clear this with !clear (or !dead, which also advances Tunum).
#   active: Boolean that tracks whether there are currently valid buzzes on a TU.
#   reader: Discord Member who is reading/moderating a given Instance.
#   bonusEnabled: Boolean that controls whether the bot will prompt for bonus points. Can be toggled with !bonusmode.
#   bonusMode: Boolean that tracks if reader is currently reading a bonus. Automatically set upon points being awarded for a TU or bonus.
#   lastBonusMem: Discord Member who last gained points on a TU. If they are on a team, whatever they get on the bonus is given to their team. Otherwise, it's added to their score.
#   red/blue/.../purpleTeam: Arrays of Discord Members from each team.
#   red/blue/.../purpleNeg: Booleans tracking if a team is locked out from buzzing due to a member of their team negging.
#   red/blue/.../purpleBonus: The number of points each team has earned on bonuses so far.
class Instance: # instance of an active game. Every channel a game is run in gets its own instance. You cannot have more than one game per channel.
    def __init__(self, channel):
        self.channel = channel
        self.TUnum = 0
        self.scores = {}
        self.buzzes = deque()
        self.buzzed = deque()
        self.active = False
        self.reader = None
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
        self.redBonus = 0
        self.blueBonus = 0
        self.greenBonus = 0
        self.orangeBonus = 0
        self.yellowBonus = 0
        self.purpleBonus = 0

    def getChannel(self):
        """Return the channel of a given Instance."""
        return self.channel
        
    def buzz(self, mem):
        """Adds a buzzing player to the buzzes and buzzed arrays, if they are allowed to buzz."""
        if self.hasBuzzed(mem):
            print("Extra")
        else:
            self.active = True
            self.buzzes.append(mem)
            self.buzzed.append(mem)
            print("Appended")
    
    def hasBuzzed(self, mem):
        """Returns whether a player has already buzzed. Returns True if they have already buzzed, and cannot do so again; False otherwise."""
        if mem in self.buzzed:
            return True
        else:
            return False
    
    def clear(self):
        """Clears the buzzes and buzzed arrays, allowing all players to buzz in once more."""
        print("Clearing...")
        self.buzzes = deque()
        self.buzzed = deque()
        self.unlock()
        
    def unlock(self):
        """Allows all teams to buzz in again."""
        print("Unlocking...")
        self.redNeg = False
        self.blueNeg = False
        self.greenNeg = False
        self.orangeNeg = False
        self.yellowNeg = False
        self.purpleNeg = False
    
    def canBuzz(self, mem):
        """Checks if a player is allowed to buzz. This exists alongside hasBuzzed() to allow for team functionality."""
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
    
    def inTeam(self, mem):
        """When bonus mode is enabled, this method reports the team of the buzzer."""
        if mem in self.redTeam:
            return "Red Team"
        if mem in self.blueTeam:
            return "Blue Team"
        if mem in self.greenTeam:
            return "Green Team"
        if mem in self.orangeTeam:
            return "Orange Team"
        if mem in self.yellowTeam:
            return "Yellow Team"
        if mem in self.purpleTeam:
            return "Purple Team"
        return "None"
    
    def teamScore(self, team, teamBonus):
        """Returns a team's total score, including bonus points."""
        total = teamBonus
        for mem in team:
            if mem in self.scores:
                total += self.scores[mem]
        return total
    
    def teamExist(self, team):
        """Checks if a given team has members"""
        if len(team) > 0:
            return True
        return False
    
    def gain(self, points):
        """Awards points to whomever last buzzed in. 
        If the points awarded is a positive number, they have gotten a TU correct, so it moves on to a bonus if those are enabled. Returns true.
        If the points awarded is a negative number or 0, they have gotten a TU incorrect, so it adds that to the individual's score and does not advance TUnum. Returns false.
        """
        awarded = False
        if self.active == True:
            mem = self.buzzes.popleft()
            if points > 0: # Someone got a TU correct.
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
                self.TUnum +=1 # If a positive # of points has been assigned, that means someone got the TU correct. Advance the TU count.
                if self.bonusEnabled:
                    self.lastBonusMem = mem
                    self.bonusMode = True # Move on to awarding bonus points
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
        """Awards bonus points, either to the team or to the individual if playing without teams."""
        if not self.bonusEnabled:
            return
        if not self.bonusMode:
            return
        conditions = (
            self.lastBonusMem in self.redTeam,
            self.lastBonusMem in self.blueTeam,
            self.lastBonusMem in self.greenTeam,
            self.lastBonusMem in self.orangeTeam,
            self.lastBonusMem in self.yellowTeam,
            self.lastBonusMem in self.purpleTeam
            )
        if any(conditions):
            if self.lastBonusMem in self.redTeam:
                self.redBonus += points
            if self.lastBonusMem in self.blueTeam:
                self.blueBonus += points
            if self.lastBonusMem in self.greenTeam:
                self.greenBonus += points
            if self.lastBonusMem in self.orangeTeam:
                self.orangeBonus += points
            if self.lastBonusMem in self.yellowTeam:
                self.yellowBonus += points
            if self.lastBonusMem in self.purpleTeam:
                self.purpleBonus += points
        else:
            self.scores[self.lastBonusMem] += points
        self.bonusMode = False
        
    def bonusStop(self):
        """Kills an active bonus."""
        if self.bonusEnabled:
            self.lastBonusMem = None
            self.bonusMode = False
        else:
            return
    
games = [] # Array holding all active games


@client.event
async def on_ready():
    """Ready message for when the bot is online."""
    await client.change_presence(activity=discord.Game(name='Ready to play!'))
    print("Quizbowl Bot online!")

@client.event
async def on_message(text):
    """Handles all commands the bot considers valid. Scans all messages, so long as they are not from bots, to see if those messages start with a valid command."""
    report = ""
    text.content=text.content.lower()
    current = text.channel.id
    exist = False
    #print(text.content)
    if text.author.bot == False:
        if text.content.startswith('!summon') or text.content.startswith('!call'):
            print("calling summon")
            if text.author.guild_permissions.administrator:
                await text.channel.send("@everyone Time for practice!")
            else:
                await text.channel.send("This command is only usable by server admins!")
        
        if text.content.startswith('!team '): # Teams require the following roles: Team red, Team blue, Team green, Team orange, Team yellow, Team purple
            print("calling team")
            report = "Invalid role!"
            #exist = False
            #for i in range(len(games)):
                #if current == games[i].getChannel():
                    #exist = True
            if text.content.startswith('!team r'):
                role = get(text.guild.roles, name = 'Team red')
                await text.author.add_roles(role)
                report = "Gave you the role, " + text.author.mention + "."
                #games[i].redTeam.append(text.author)
            if text.content.startswith('!team b'):
                role = get(text.guild.roles, name = 'Team blue')
                await text.author.add_roles(role)
                report = "Gave you the role, " + text.author.mention + "."
                #games[i].blueTeam.append(text.author)
            if text.content.startswith('!team g'):
                role = get(text.guild.roles, name = 'Team green')
                await text.author.add_roles(role)
                report = "Gave you the role, " + text.author.mention + "."
                #games[i].greenTeam.append(text.author)
            if text.content.startswith('!team o'):
                role = get(text.guild.roles, name = 'Team orange')
                await text.author.add_roles(role)
                report = "Gave you the role, " + text.author.mention + "."
                #games[i].orangeTeam.append(text.author)
            if text.content.startswith('!team y'):
                role = get(text.guild.roles, name = 'Team yellow')
                await text.author.add_roles(role)
                report = "Gave you the role, " + text.author.mention + "."
                #games[i].yellowTeam.append(text.author)
            if text.content.startswith('!team p'):
                role = get(text.guild.roles, name = 'Team purple')
                await text.author.add_roles(role)
                report = "Gave you the role, " + text.author.mention + "."
                #games[i].purpleTeam.append(text.author)
                    #break
            #if exist == False:
                #report = "You need to start a game first! Use '!start' to start a game."
            await text.channel.send(report)
    
        if text.content.startswith('!start') or text.content.startswith('!begin'):
            print("calling start")
            for i in range(len(games)):
                if current == games[i].getChannel():
                    exist = True
                    break
            if exist == False:
                report = ("Starting a new game. Reader is " + text.author.mention + ".")
                x = Instance(current)
                x.reader = text.author
                print(x.getChannel())
                role = get(text.guild.roles, name = 'reader') # The bot needs you to make a role called "reader" in order to function.
                await text.author.add_roles(role)
                games.append(x)
            else:
                report = "You already have an active game in this channel."
            await text.channel.send(report)
        
        if text.content.startswith('!newreader'):
            print("calling newreader")
            for i in range(len(games)):
                if current == games[i].getChannel():
                    exist = True
                    if text.author == games[i].reader:
                        report + "You are already the reader, " + text.author.mention + "!"
                    else:
                        report = "Removed reader role from " + games[i].reader.mention + ". Gave reader role to " + text.author.mention + "."
                        role = get(text.guild.roles, name = 'reader')
                        await games[i].reader.remove_roles(role)
                        games[i].reader = text.author
                        await text.author.add_roles(role)
                    break
            if exist ==False:
                report = "You need to start a game first! Use '!start' to start a game."
            await text.channel.send(report)
        
        if text.content.startswith('!end') or text.content.startswith('!stop'):
            print("calling end")
            for i in range(len(games)):
                if current == games[i].getChannel():
                    exist = True
                    if text.author.id == games[i].reader.id:
                        games.pop(i)
                        report = "Ended the game active in this channel."
                        role = get(text.guild.roles, name = 'reader')
                        await text.author.remove_roles(role)
                    else:
                        report = "You are not the reader!"
                    break
            if exist == False:
                report = "You do not currently have an active game."
            await text.channel.send(report)
                
        if text.content.startswith('!dead'):
            print("calling dead")
            for i in range(len(games)):
                if current == games[i].getChannel():
                    exist = True
                    if text.author.id == games[i].reader.id:
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
            for i in range(len(games)):
                if current == games[i].getChannel():
                    exist = True
                    if text.author.id == games[i].reader.id:
                        games[i].clear()
                        report = "Buzzers cleared, anyone can buzz."
                        break
                    else:
                        report = "You are not the reader!"
            if exist == False:
                report = "You need to start a game first! Use '!start' to start a game."
            await text.channel.send(report)
        
        if len(games) != 0 and isInt(text.content): # Assigns points. Checks len games to avoid unnecessary calls.
            print("calling points")
            print(text.content + " is an int")
            if text.content.startswith('<:neg:'): # This and the next two conditional check to see if someone is using a valid emoji to assign points. While, to the user, an emoji looks like :emojiName:, to the bot it is also wrapped in <>.
                text.content = "-5"
            if text.content.startswith('<:ten:'):
                text.content = "10"
            if text.content.startswith('<:power:'):
                text.content = "15"
            for i in range(len(games)):
                if current == games[i].getChannel():
                    exist = True
                    #reader = get(text.guild.roles, name = 'reader')
                    if text.author.id == games[i].reader.id:
                        if games[i].bonusEnabled == False:
                            if games[i].gain(int(text.content)):
                                await text.channel.send("Awarded points. Next TU.")
                            else:
                                while len(games[i].buzzes) > 0:
                                    if games[i].canBuzz(games[i].buzzes[0]):
                                        await text.channel.send((games[i].buzzes[0]).mention + " buzzed. Pinging reader: " + str(games[i].reader.mention))
                                        break
                                    else:
                                        games[i].buzzes.popleft()
                        else: #bonuses enabled
                            if games[i].bonusMode == False:
                                if games[i].gain(int(text.content)):
                                    report = "Awarded TU points. "
                                    getTeam = games[i].inTeam(text.author)
                                    if getTeam != "None":
                                        report += "Bonus is for " + getTeam + ". "
                                    report +=  "Awaiting bonus points."
                                    await text.channel.send(report)
                                else:
                                    while len(games[i].buzzes) > 0:
                                        if games[i].canBuzz(games[i].buzzes[0]):
                                            await text.channel.send((games[i].buzzes[0]).mention + " buzzed. Pinging reader: " + str(games[i].reader.mention))
                                            break
                                        else:
                                            games[i].buzzes.popleft()
                            else: #bonusMode true
                                games[i].bonusGain(int(text.content))
                                await text.channel.send("Awarded bonus points. Next TU.")
                    break
        
        if text.content.startswith('wd') or text.content.startswith('!wd') or text.content.startswith('withdraw') or text.content.startswith('!withdraw'):
            print("calling withdraw")
            for i in range(len(games)):
                if current == games[i].getChannel():
                    exist = True
                    if games[i].buzzes[0] == text.author:
                        games[i].buzzes.popleft()
                        newBuzzed = deque()
                        while len(games[i].buzzed) > 0:
                            if games[i].buzzed[0] == text.author:
                                games[i].buzzed.popleft()
                            else:
                                newBuzzed.append(games[i].buzzed.popleft())
                        games[i].buzzed = newBuzzed
                        report = "Withdrew " + text.author.mention + "'s buzz. "
                        while len(games[i].buzzes) > 0:
                            if games[i].canBuzz(games[i].buzzes[0]):
                                report += (games[i].buzzes[0]).mention + " buzzed. Pinging reader: " + str(games[i].reader.mention)
                                break
                            else:
                                games[i].buzzes.popleft()
                        await text.channel.send(report)
                        break
                    else:
                        await text.channel.send("Only the currently recognized player can withdraw.")
                        break
                    break
            if exist == False:
                await text.channel.send("You need to start a game first! Use '!start' to start a game.")
        
        if text.content.startswith('!bonusmode') or text.content.startswith('!btoggle'): # Toggles whether bonus mode is enabled. It is enabled by default.
            print("calling bonusmode")
            for i in range(len(games)):
                if current == games[i].getChannel():
                    exist = True
                    if text.author.id == games[i].reader.id or text.author.guild_permissions.administrator:
                        games[i].bonusStop()
                        games[i].bonusEnabled = not games[i].bonusEnabled
                        if games[i].bonusEnabled:
                            await text.channel.send("Enabled bonus mode.")
                        else:
                            await text.channel.send("Disabled bonus mode.")
                    break
            if exist == False:
                await text.channel.send("You need to start a game first! Use '!start' to start a game.")
        
        if text.content.startswith('!bstop'): # Ends current bonus round. Use this to kill a bonus without giving points.
            print("calling bstop")
            for i in range(len(games)):
                if current == games[i].getChannel():
                    exist = True
                    if text.author.id == games[i].reader.id:
                        games[i].bonusStop()
                        await text.channel.send("Killed active bonus. Next TU.")
                    break
        
        if text.content.startswith('!score'):
            print("calling score")
            names = []
            diction = {}
            for i in range(len(games)):
                if current == games[i].getChannel():
                    exist = True
                    areTeams = False
                    desc = "Score after TU# " + str(games[i].TUnum) + ": "
                    
                    #The following seven conditionals modify the scoreboard to include team scores, if those teams exist.
                    if games[i].teamExist(games[i].redTeam):
                        desc += "\r\nRed team: " + str(games[i].teamScore(games[i].redTeam, games[i].redBonus))
                        areTeams = True
                    if games[i].teamExist(games[i].blueTeam):
                        desc += "\r\nBlue team: " + str(games[i].teamScore(games[i].blueTeam, games[i].blueBonus))
                        areTeams = True
                    if games[i].teamExist(games[i].greenTeam):
                        desc += "\r\nGreen team: " + str(games[i].teamScore(games[i].greenTeam, games[i].greenBonus))
                        areTeams = True
                    if games[i].teamExist(games[i].orangeTeam):
                        desc += "\r\nOrange team: " + str(games[i].teamScore(games[i].orangeTeam, games[i].orangeBonus))
                        areTeams = True
                    if games[i].teamExist(games[i].yellowTeam):
                        desc += "\r\nYellow team: " + str(games[i].teamScore(games[i].yellowTeam, games[i].yellowBonus))
                        areTeams = True
                    if games[i].teamExist(games[i].purpleTeam):
                        desc += "\r\nPurple team: " + str(games[i].teamScore(games[i].purpleTeam, games[i].purpleBonus))
                        areTeams = True
                    if areTeams:
                        desc += "\r\n\r\nIndividuals:"
                        
                    emb = discord.Embed(title="Score", description=desc, color=0x57068C)
                    for x,y in games[i].scores.items():
                        if x.nick == 'none' or x.nick == 'None' or x.nick == None: # Tries to display the Member's Discord nickname if possible, but if none exists, displays their username.
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
                        emb.add_field(name=(str(i+1) + ". " + names[limit-(i+1)]), value=str(sortedDict[names[limit-(i+1)]]), inline=True)
                    await text.channel.send(embed=emb)
                    break
            if exist == False:
                report = "You need to start a game first! Use '!start' to start a game."
                await text.channel.send(report)
    
        if isBuzz(text.content):
            print("calling buzz")
            for i in range(len(games)):
                if current == games[i].getChannel():
                    exist = True
                    #reader = get(text.guild.roles, name = 'reader')
                    
                    # This block handles all team assignment that was done before the game started.
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
                            if games[i].canBuzz(text.author):
                                if len(games[i].buzzes) < 1:
                                    games[i].buzz(text.author)
                                    print("Buzzed!")
                                    report = str(text.author.mention) + " buzzed. Pinging reader: " + str(games[i].reader.mention)
                                    await text.channel.send(report)
                                else:
                                    games[i].buzz(text.author)
                                    print("Buzzed!")
                            else: # Might want to remove this if it causes too much clutter.
                                await text.channel.send("Your team is locked out of buzzing, " + str(text.author.mention) + ".")
                    else:
                        await text.channel.send("We are currently playing a bonus. You cannot buzz.")
                    break
            if exist == False:
                report = "You need to start a game first! Use '!start' to start a game."
                await text.channel.send(report)
    
        if text.content.startswith('!github'):
            print("calling github")
            emb = discord.Embed(title="Lev's Quizbowl Bot", description="", color=0x57068C)
            #await text.channel.send("https://github.com/LevBernstein/LevQuizbowlBot")
            emb.add_field(name= "View this bot's source code at:", value= "https://github.com/LevBernstein/LevQuizbowlBot", inline=True)
            await text.channel.send(embed=emb)
            
        if text.content.startswith('!report'):
            print("calling report")
            emb = discord.Embed(title="Report bugs or suggest features", description="", color=0x57068C)
            #await text.channel.send("Report any issues at:\r\nhttps://github.com/LevBernstein/LevQuizbowlBot/issues")
            emb.add_field(name= "Report any issues at:", value= "https://github.com/LevBernstein/LevQuizbowlBot/issues", inline=True)
            await text.channel.send(embed=emb)
    
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
            emb.add_field(name= "!newreader", value= "Removes the reader role from the old reader and designates you the new reader.", inline=True)
            emb.add_field(name= "!call", value= "Mentions everyone in the server and informs them that it is time for practice. Usable only by admins.", inline=True)
            emb.add_field(name= "!github", value= "Gives you a link to this bot's github page.", inline=True)
            emb.add_field(name= "!report", value= "Gives you a link to this bot's issue-reporting page.", inline=True)
            emb.add_field(name= "!tu", value= "Reports the current tossup number.", inline=True)
            emb.add_field(name= "!bonusmode", value= "Disables or enables bonuses. Bonuses are enabled by default.", inline=True)
            emb.add_field(name= "!bstop", value= "Kills an active bonus without giving points.", inline=True)
            emb.add_field(name= "!team [r/b/g/o/y/p]", value= "Assigns you the team role corresponding to the color you entered.", inline=True)
            emb.add_field(name= "wd", value= "Withdraws a buzz.", inline=True)
            emb.add_field(name= "!tutorial", value= "Shows you this list.", inline=True)
            emb.add_field(name= "_ _", value= "_ _", inline=True) # filler for formatting
            await text.channel.send(embed=emb)
            
            #await text.channel.send('Valid commands: \r\n "!start" starts a new game. \r\n "buzz" buzzes in. \r\n Enter any positive or negative whole number after someone buzzes to assign points. \r\n "!clear" clears buzzers after a TU goes dead. \r\n "!score" displays the score, sorted from highest to lowest. \r\n "!end" ends the active game. \r\n "!team [red/blue/green/orange/yellow/purple]" assigns you the team role corresponding to the color you entered. \r\n "!call" or "!summon" mentions everyone in the server and informs them it is time for practice \r\n "!github" gives you a link to this bot\'s github page. \r\n "!report" gives you a link to this bot\'s issue-reporting page. ')

        elif text.content.startswith('!tu') or text.content.startswith('!tunum'): # elif because otherwise !tutorial calls this too
            print("calling tu")
            for i in range(len(games)):
                if current == games[i].getChannel():
                    exist = True
                    report = "Current TU: #" + str(games[i].TUnum + 1) + "."
            if exist == False:
                report = "You need to start a game first! Use '!start' to start a game."
            await text.channel.send(report)

        if text.content.startswith('!export'):
            #TODO export score to CSV. Requires tracking score for each TU and switching bonuses to a binary system a la online scoresheets made by Ophir
            for i in range(len(games)):
                if current == games[i].getChannel():
                    exist = True
                    exportedTime = str(datetime.now())[:-5]
                    emb = discord.Embed(title="Exported scoresheet at " + exportedTime + ".", description="", color=0x57068C)
                    emb.add_field(name = "This feature has not been implemented yet!", value= "Make sure to check https://github.com/LevBernstein/LevQuizbowlBot for updates!", inline=False)
                    await text.channel.send(embed=emb)
            if exist == False:
                await text.channel.send("You need to start a game first! Use '!start' to start a game.")

client.run(token)
