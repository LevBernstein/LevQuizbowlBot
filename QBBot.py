# Lev's Quizbowl Bot
# Author: Lev Bernstein
# Version: 1.6.0
# This bot is designed to be a user-friendly Quizbowl Discord bot with a minimum of setup.
# All commands are documented; if you need any help understanding them, try the command !tutorial.
# This bot is free software, licensed under the GNU GPL version 3. If you want to modify the bot in any way,
# you are absolutely free to do so. If you make a change you think others would enjoy, I'd encourage you to
# make a pull request on the bot's GitHub page (https://github.com/LevBernstein/LevQuizbowlBot).

from __future__ import print_function
from time import sleep
from datetime import datetime, date, timezone
import random as random
import operator
from collections import deque, OrderedDict
import copy
#import pickle
#import os.path


import discord
from discord.ext import commands
from discord.utils import get

#from googleapiclient.discovery import build
#from google_auth_oauthlib.flow import InstalledAppFlow
#from google.auth.transport.requests import Request



# Setup
f = open("token.txt", "r") # in token.txt, paste in your own Discord API token
token = f.readline()
generateLogs = True # if the log files are getting to be too much for you, set this to False
client = discord.Client()

# Global helper methods
def isInt(st):
    """Checks if an entered string would be a valid number of points to assign."""
    if len(st) == 0: # this conditional handles an issue with the bot trying to interpret attached images as strings
        return False
    if st.startswith('<:ten:') or st.startswith('<:neg:') or st.startswith('<:power:'): # this conditional handles awarding points with emojis
        return True
    if st[0] == '-' or st[0] == '+':
        return st[1:].isdigit()
    return st.isdigit()

def isBuzz(st):
    """Checks if an entered string is a valid buzz."""
    validBuzzes = (
        st.startswith('buz'),
        st.startswith('<:buzz:'),
        st.startswith('bz'),
        st.startswith('!bz'),
        st.startswith('!buz'),
        st.startswith('<:bee:'),
        )
    if any(validBuzzes):
        return True
    return False


#############################################################
# Backup(self, prev)
# This class is a backup of previous scores, for the purpose of being able to undo an incorrect points assignment.
# It is essentially a singly linked list with some additional data fields.
# Parameters: prev is the previous backup of the scores.
class Backup:
    def __init__(self, prev):
        # TODO store TUnum here as well, to better handle negs
        self.scores = {}
        self.redBonus = 0
        self.blueBonus = 0
        self.greenBonus = 0
        self.orangeBonus = 0
        self.yellowBonus = 0
        self.purpleBonus = 0
        self.TUnum = 0
        self.lastNeg = False
        self.prev = prev

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
#   logFile: A log created to track all commands from this particular game. Untracked by .gitignore.
#   lastNeg: Boolean that tracks whether the last buzz was a 0/-5. Used in undo.
#   oldScores: A Backup() of a given Instance's scores.
class Instance: # instance of an active game. Each channel a game is run in gets its own instance. You cannot have more than one game per channel.
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
        #self.logFile = open(("gamelogs/" + str(self.getChannel())[-5:] + "-" + datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".log"), "a")
        #self.csvScore = open(("gamelogs/" + str(self.getChannel())[-5:] + "-" + datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".csv"), "a")
        self.logFile = ("gamelogs/" + str(self.getChannel())[-5:] + "-" + datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".log")
        self.csvScore = ("gamelogs/" + str(self.getChannel())[-5:] + "-" + datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".csv")
        # log and scoresheet filename format: channelID-YYYY-mm-DD-HH-MM-SS
        self.lastNeg = False
        self.oldScores = Backup(None)

    def getChannel(self):
        """Return the channel of a given Instance. 
        TODO For the sake of proper encapsulation, to make my CS101 professor proud, I should switch to method calls like this for every local variable I access in on_message().
        """
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
        return False
    
    def clear(self):
        """Clears the buzzes and buzzed arrays, allowing all players to buzz in once more."""
        print("Clearing...")
        self.buzzes = deque()
        self.buzzed = deque()
        self.unlock()
        self.active = False
    
    def dead(self):
        temp = copy.copy(self.oldScores)
        self.oldScores.prev = temp
        self.oldScores.scores = copy.copy(self.scores)
        self.oldScores.redBonus = self.redBonus
        self.oldScores.blueBonus = self.blueBonus
        self.oldScores.greenBonus = self.greenBonus
        self.oldScores.orangeBonus = self.orangeBonus
        self.oldScores.yellowBonus = self.yellowBonus
        self.oldScores.purpleBonus = self.purpleBonus
        self.oldScores.TUnum = self.TUnum
        self.oldScores.lastNeg = self.lastNeg
        self.clear()
        self.lastNeg = False
        self.TUnum +=1
    
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
        """Checks if a player's team is allowed to buzz.
        This exists alongside hasBuzzed() to reflect the two different reasons for not being allowed to buzz:
        Having personally negged, or a teammate having negged. canBuzz() checks if a teammate has negged.
        """
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
    
    def undo(self):
        """Reverts scores back to one tossup ago."""
        self.scores = copy.copy(self.oldScores.scores)
        self.redBonus = self.oldScores.redBonus
        self.blueBonus = self.oldScores.blueBonus
        self.greenBonus = self.oldScores.greenBonus
        self.orangeBonus = self.oldScores.orangeBonus
        self.yellowBonus = self.oldScores.yellowBonus
        self.purpleBonus = self.oldScores.purpleBonus
        self.oldScores = self.oldScores.prev
        self.TUnum = self.oldScores.TUnum
        """
        if self.lastNeg:
            self.TUnum += 1
            self.oldScores.TUnum += 1
        """
        self.lastNeg = self.oldScores.lastNeg
        self.clear()
        
    def gain(self, points):
        """Awards points to the player at the front of the buzzes queue. 
        If the points awarded is a positive number, they have gotten a TU correct, so it moves on to a bonus if those are enabled. Returns true.
        If the points awarded is a negative number or 0, they have gotten a TU incorrect, so it adds that to the individual's score and does not advance TUnum. Returns false.
        Rarely, a pickling error arises with the backup system; might have fixed by switching to copy from deepcopy.
        """
        awarded = False
        if self.active == True:
            mem = self.buzzes.popleft()
            temp = copy.copy(self.oldScores)
            self.oldScores.prev = temp
            self.oldScores.scores = copy.copy(self.scores)
            self.oldScores.redBonus = self.redBonus
            self.oldScores.blueBonus = self.blueBonus
            self.oldScores.greenBonus = self.greenBonus
            self.oldScores.orangeBonus = self.orangeBonus
            self.oldScores.yellowBonus = self.yellowBonus
            self.oldScores.purpleBonus = self.purpleBonus
            self.oldScores.TUnum = self.TUnum
            self.oldScores.lastNeg = self.lastNeg
            if points > 0: # Someone got a TU correct.
                self.lastNeg = False
                if mem in self.scores:
                    self.scores[mem] = self.scores[mem] + points
                    self.active = False
                    self.clear()
                    awarded = True
                else:
                    with open(self.csvScore) as f:
                        body = f.readlines()
                    body[0] += mem.name + ","
                    with open(self.csvScore, "w") as f:
                        f.writelines(body)
                    self.scores[mem] = points
                    self.active = False
                    self.clear()
                    awarded = True
                
                if self.bonusEnabled:
                    self.lastBonusMem = mem
                    self.bonusMode = True # Move on to awarding bonus points
            else: #Someone got a 0 or a -5.
                self.lastNeg = True
                if mem in self.scores:
                    self.scores[mem] = self.scores[mem] + points
                else:
                    self.scores[mem] = points
                if len(self.buzzes) == 0:
                    self.active = False
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
            
            with open(self.csvScore) as f:
                body = f.readlines()
                subMems = body[0].split(',')
                found = False
                for i in range(len(subMems)):
                    if mem.name == subMems[i]:
                        spot = i
                        found = True
                        break
            if found:
                newLine = "\r\n" + str(self.TUnum)
                for i in range (spot):
                    newLine += " ,"
                newLine += str(points) + ","
                with open(self.csvScore, "a") as f:
                    f.write(newLine)
        
        if awarded:
            self.TUnum +=1 # If a positive # of points has been assigned, that means someone got the TU correct. Advance the TU count.
        return awarded

    def bonusGain(self, points):
        """Awards bonus points, either to the team or to the individual if playing without teams."""
        if not self.bonusEnabled:
            return
        if not self.bonusMode:
            return
        temp = copy.copy(self.oldScores)
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
            print("Could not stop a bonus!")
    
games = [] # Array holding all active games


@client.event
async def on_ready():
    """Ready message for when the bot is online."""
    await client.change_presence(activity=discord.Game(name='Ready to play QB!'))
    print("Activity live!")
    print("Quizbowl Bot online!")

@client.event
async def on_message(text):
    """Handles all commands the bot considers valid. Scans all messages, so long as they are not from bots, to see if those messages start with a valid command."""
    report = "" # report is usually what the bot sends in response to valid commands, and, in case a game is active, it is what the bot write to that game's log file.
    text.content=text.content.lower() # for ease of use, all commands are lowercase, and all messages scanned are converted to lowercase.
    current = text.channel.id
    exist = False
    heldGame = None
    botSpoke = False
    print(str(current) + " " + str(datetime.now())[:-5] + " " + text.author.name + ": " + text.content) # for an even more detailed log than the log files, check your console. This prints every message.
    if text.author.bot == False:
        for i in range(len(games)):
            if current == games[i].getChannel():
                exist = True
                heldGame = games[i]
                break
        
        if text.content.startswith('!setup'):
            """Run this command once, after you add the bot the your server. It will handle all role and emoji creation, and set the bot's avatar.
            Please avoid running this command more than once, as doing so will create duplicate emojis. If for whatever reason you have to do so, that's fine, just be prepared to delete those emojis.'
            """
            report = "This command is only usable by server admins!"
            if text.author.guild_permissions.administrator: # Bot setup requires admin perms.
                await text.channel.send("Starting setup...")
                # This block handles role creation. The bot requires these roles to function, so if you don't make them, the bot will.
                willHoist = True # Hoist makes it so that a given role is displayed separately on the sidebar.
                if not get(text.guild.roles, name = 'Reader'):
                    await text.guild.create_role(name = 'Reader', colour = discord.Colour(0x01ffdd), hoist = willHoist)
                    print("Created Reader.")
                if not get(text.guild.roles, name = 'Team red'):
                    await text.guild.create_role(name = 'Team red', colour = discord.Colour(0xf70a0a), hoist = willHoist)
                    print("Created Team red.")
                if not get(text.guild.roles, name = 'Team blue'):
                    await text.guild.create_role(name = 'Team blue', colour = discord.Colour(0x009ef7), hoist = willHoist)
                    print("Created Team blue.")
                if not get(text.guild.roles, name = 'Team green'):
                    await text.guild.create_role(name = 'Team green', colour = discord.Colour(0x7bf70b), hoist = willHoist)
                    print("Created Team green.")
                if not get(text.guild.roles, name = 'Team orange'):
                    await text.guild.create_role(name = 'Team orange', colour = discord.Colour(0xff6000), hoist = willHoist)
                    print("Created Team orange.")
                if not get(text.guild.roles, name = 'Team yellow'):
                    await text.guild.create_role(name = 'Team yellow', colour = discord.Colour(0xfeed0e), hoist = willHoist)
                    print("Created Team yellow.")
                if not get(text.guild.roles, name = 'Team purple'):
                    await text.guild.create_role(name = 'Team purple', colour = discord.Colour(0xb40eed), hoist = willHoist)
                    print("Created Team purple.")
                print("Roles live!")
                
                # This block creates the emojis the bot accepts for points and buzzes. Credit for these wonderful emojis goes to Theresa Nyowheoma, President of Quiz Bowl at NYU, 2020-2021.
                with open("templates/emoji/buzz.png", "rb") as buzzIMG:
                    img = buzzIMG.read()
                    await text.guild.create_custom_emoji(name = 'buzz', image = img)
                with open("templates/emoji/neg.png", "rb") as negIMG:
                    img = negIMG.read()
                    await text.guild.create_custom_emoji(name = 'neg', image = img)
                with open("templates/emoji/ten.png", "rb") as tenIMG:
                    img = tenIMG.read()
                    await text.guild.create_custom_emoji(name = 'ten', image = img)
                with open("templates/emoji/power.png", "rb") as powerIMG:
                    img = powerIMG.read()
                    await text.guild.create_custom_emoji(name = 'power', image = img)
                print("Emojis live!")
                
                g = open("templates/pfp.png", "rb")
                pic = g.read()
                await client.user.edit(avatar=pic)
                print("Avatar live!")
    
                report = "Successfully set up the bot! Team roles now exist, as do the following emojis: buzz, power, ten, neg."
            await text.channel.send(report)
        
        if text.content.startswith('!summon') or text.content.startswith('!call'):
            print("calling summon")
            botSpoke = True
            report = "This command is only usable by server admins!"
            if text.author.guild_permissions.administrator: # this makes sure people can't just ping everyone in the server whenever they want. Only admins can do that.
                report = "@everyone Time for practice!"
            await text.channel.send(report)
    
        if text.content.startswith('!start') or text.content.startswith('!begin') or text.content.startswith('!read'):
            botSpoke = True
            print("calling start")
            if exist:
                report = "You already have an active game in this channel."
            else:
                role = get(text.guild.roles, name = 'Reader') # The bot needs you to make a role called "Reader" in order to function.
                if role:
                    report = "Starting a new game. Reader is " + text.author.mention + "."
                    x = Instance(current)
                    x.reader = text.author
                    print(x.getChannel())
                    await text.author.add_roles(role)
                    heldGame = x
                    with open(x.logFile, "a") as f:
                        f.write("Start of game in channel " + str(current) + " at " + datetime.now().strftime("%H:%M:%S") + ".\r\n\r\n")
                    with open(x.csvScore, "a") as f:
                        f.write("TU#,")
                    games.append(x)
                else:
                    report = "You need to run !setup before you can start a game."
            await text.channel.send(report)
        
        if text.content.startswith('!newreader'):
            """Use this to set yourself as the new reader in an already-active game.
            TODO Write a targeted form of this command, allowing you to set someone else as the new reader. Requires get_member(), and therefore __init__ with intents.members(), chunk_guilds_at_startup, fetch_all_members
            """
            print("calling newreader")
            botSpoke = True
            report = "You need to start a game first! Use '!start' to start a game."
            if exist:
                if text.author == heldGame.reader:
                    report = "You are already the reader, " + text.author.mention + "!"
                else:
                    report = "Removed reader role from " + heldGame.reader.mention + ". Gave reader role to " + text.author.mention + "."
                    role = get(text.guild.roles, name = 'Reader')
                    await heldGame.reader.remove_roles(role)
                    heldGame.reader = text.author
                    await text.author.add_roles(role)
            await text.channel.send(report)
        
        if text.content.startswith('!end') or text.content.startswith('!stop'):
            # TODO make end autoexport scoresheet
            print("calling end")
            botSpoke = True
            report = "You do not currently have an active game."
            for i in range(len(games)):
                if current == games[i].getChannel():
                    exist = True
                    heldGame = games[i]
                    if text.author.id == games[i].reader.id or text.author.guild_permissions.administrator:
                        games.pop(i)
                        report = "Ended the game active in this channel."
                        role = get(text.guild.roles, name = 'Reader')
                        await text.author.remove_roles(role)
                    else:
                        report = "You are not the reader!"
                    break
            await text.channel.send(report)
        
        # DEPRECATED until I figure out the issue with TUnum tracking.
        if text.content.startswith('!undo'):
            print("calling undo")
            botSpoke = True
            report = "You need to start a game first! Use '!start' to start a game."
            if exist:
                if text.author.id == heldGame.reader.id:
                    if heldGame.bonusMode:
                        report = "Finish your bonus first!"
                    else:
                        if heldGame.active:
                            report = "Assign TU points first!"
                        else:
                            if heldGame.TUnum == 0 and len(heldGame.scores) == 0:
                                report = "Nothing to undo."
                            else:
                                heldGame.undo()
                                report = "Undid last Tossup scorechange."
                else:
                    report = "You are not the reader!"
            await text.channel.send(report)
        
        
        if text.content.startswith('!dead'):
            print("calling dead")
            botSpoke = True
            report = "You need to start a game first! Use '!start' to start a game."
            if exist:
                if text.author.id == heldGame.reader.id:
                    heldGame.dead()
                    report = "TU goes dead. Next TU."
                else:
                    report = "You are not the reader!"
            await text.channel.send(report)
        
        if text.content.startswith('!clear'):
            print("calling clear")
            botSpoke = True
            report = "You need to start a game first! Use '!start' to start a game."
            if exist:
                if text.author.id == heldGame.reader.id:
                    heldGame.clear()
                    report = "Buzzers cleared, anyone can buzz."
                else:
                    report = "You are not the reader!"
            await text.channel.send(report)
        
        if len(games) != 0 and isInt(text.content): # Assigns points. Checks len games to avoid unnecessary calls.
            print("calling points")
            print(text.content + " is an int")
            if text.content.startswith('<:neg:'): # This and the next two conditionals check to see if someone is using a valid emoji to assign points. While, to the user, an emoji looks like :emojiName:, to the bot it is also wrapped in <>.
                text.content = "-5"
            if text.content.startswith('<:ten:'):
                text.content = "10"
            if text.content.startswith('<:power:'):
                text.content = "15"
            if exist:
                botSpoke = True
                if text.author.id == heldGame.reader.id:
                    if heldGame.bonusEnabled == False:
                        if heldGame.gain(int(text.content)):
                            report = "Awarded points. Next TU."
                            await text.channel.send(report)
                        else:
                            while len(heldGame.buzzes) > 0:
                                if heldGame.canBuzz(heldGame.buzzes[0]):
                                    report = (heldGame.buzzes[0]).mention + " buzzed. Pinging reader: " + str(heldGame.reader.mention)
                                    await text.channel.send(report)
                                    break
                                else:
                                    heldGame.buzzes.popleft()
                    else: # bonuses enabled
                        if heldGame.bonusMode == False:
                            storedMem = heldGame.buzzes[0]
                            if heldGame.gain(int(text.content)):
                                report = "Awarded TU points. "
                                getTeam = heldGame.inTeam(storedMem)
                                if getTeam != "None":
                                    report += "Bonus is for " + getTeam + ". "
                                report +=  "Awaiting bonus points."
                                await text.channel.send(report)
                            else:
                                while len(heldGame.buzzes) > 0:
                                    if heldGame.canBuzz(heldGame.buzzes[0]):
                                        report = (heldGame.buzzes[0]).mention + " buzzed. Pinging reader: " + str(heldGame.reader.mention)
                                        await text.channel.send(report)
                                        break
                                    else:
                                        heldGame.buzzes.popleft()
                                        # because I don't send a report here, I can't have the text.channel.send(report) at the end; doing so throws an exception because it would be sending an empty message
                        else: # bonusMode true
                            heldGame.bonusGain(int(text.content))
                            report = "Awarded bonus points. Next TU."
                            await text.channel.send(report)
                #await text.channel.send(report)
        
        if text.content.startswith('wd') or text.content.startswith('!wd') or text.content.startswith('withdraw') or text.content.startswith('!withdraw'):
            print("calling withdraw")
            botSpoke = True
            report = "You need to start a game first! Use '!start' to start a game."
            if exist:
                if heldGame.buzzes[0] == text.author:
                    heldGame.buzzes.popleft()
                    newBuzzed = deque()
                    while len(heldGame.buzzed) > 0:
                        if heldGame.buzzed[0] == text.author:
                            heldGame.buzzed.popleft()
                        else:
                            newBuzzed.append(heldGame.buzzed.popleft())
                    heldGame.buzzed = newBuzzed
                    report = "Withdrew " + text.author.mention + "'s buzz. "
                    while len(heldGame.buzzes) > 0:
                        if heldGame.canBuzz(heldGame.buzzes[0]):
                            report += (heldGame.buzzes[0]).mention + " buzzed. Pinging reader: " + str(heldGame.reader.mention)
                            break
                        else:
                            heldGame.buzzes.popleft()
                else:
                    report = "Only the currently recognized player can withdraw." 
            await text.channel.send(report)
        
        if text.content.startswith('!bonusmode') or text.content.startswith('!btoggle'):
            """Toggles whether bonus mode is enabled. It is enabled by default."""
            print("calling bonusmode")
            botSpoke = True
            report = "You need to start a game first! Use '!start' to start a game."
            if exist:
                if text.author.id == heldGame.reader.id or text.author.guild_permissions.administrator:
                    heldGame.bonusStop()
                    heldGame.bonusEnabled = not heldGame.bonusEnabled
                    if heldGame.bonusEnabled:
                        report = "Enabled bonus mode."
                    else:
                        report = "Disabled bonus mode."
            await text.channel.send(report)
        
        if text.content.startswith('!bstop'):
            """Ends current bonus round. Use this to kill a bonus without giving points. Only use if something has gone wrong and you need to kill a bonus immediately."""
            print("calling bstop")
            botSpoke = True
            report = "You need to start a game first! Use '!start' to start a game."
            if exist:
                if text.author.id == heldGame.reader.id:
                    heldGame.bonusStop()
                    report = "Killed active bonus. Next TU."
                else:
                    report = "You are not the reader!"
            await text.channel.send(report)
        
        if text.content.startswith('!team '):
            """ Adds the user to a given team.
            Teams require the following roles: Team red, Team blue, Team green, Team orange, Team yellow, Team purple.
            If you do not have those roles in your server, the bot will create them for you when you run !setup. 
            Depending on your role hierarchy, the bot-created roles might not show their color for each user.
            Make sure that, for non-admin users, the team roles are the highest they can have in the hierarchy.
            Admin roles should still be higher than the team roles.
            """
            print("calling team")
            botSpoke = True
            report = "Invalid role!"
            rolesExist = False
            if text.content.startswith('!team r'):
                role = get(text.guild.roles, name = 'Team red')
                if role:
                    await text.author.add_roles(role)
                    report = "Gave you the role, " + text.author.mention + "."
                    rolesExist = True
            if text.content.startswith('!team b'):
                role = get(text.guild.roles, name = 'Team blue')
                if role:
                    await text.author.add_roles(role)
                    report = "Gave you the role, " + text.author.mention + "."
                    rolesExist = True
            if text.content.startswith('!team g'):
                role = get(text.guild.roles, name = 'Team green')
                if role:
                    await text.author.add_roles(role)
                    report = "Gave you the role, " + text.author.mention + "."
                    rolesExist = True
            if text.content.startswith('!team o'):
                role = get(text.guild.roles, name = 'Team orange')
                if role:
                    await text.author.add_roles(role)
                    report = "Gave you the role, " + text.author.mention + "."
                    rolesExist = True
            if text.content.startswith('!team y'):
                role = get(text.guild.roles, name = 'Team yellow')
                if role:
                    await text.author.add_roles(role)
                    report = "Gave you the role, " + text.author.mention + "."
                    rolesExist = True
            if text.content.startswith('!team p'):
                role = get(text.guild.roles, name = 'Team purple')
                if role:
                    await text.author.add_roles(role)
                    report = "Gave you the role, " + text.author.mention + "."
                    rolesExist = True
            if not rolesExist:
                report = "Uh-oh! The Discord role you are trying to add does not exist! If whoever is going to read does !start, I will create the roles for you."
            await text.channel.send(report)
        
        if text.content.startswith('!score'):
            print("calling score")
            botSpoke = True
            names = []
            diction = {}
            if exist:
                areTeams = False
                if len(heldGame.scores) == 0:
                    desc = "Score at start of game:"
                else:
                    desc = "Score after " + str(heldGame.TUnum) + " completed TUs: "
                    #The following seven conditionals modify the scoreboard to include team scores, if those teams exist.
                    if heldGame.teamExist(heldGame.redTeam):
                        desc += "\r\nRed team: " + str(heldGame.teamScore(heldGame.redTeam, heldGame.redBonus))
                        areTeams = True
                    if heldGame.teamExist(heldGame.blueTeam):
                        desc += "\r\nBlue team: " + str(heldGame.teamScore(heldGame.blueTeam, heldGame.blueBonus))
                        areTeams = True
                    if heldGame.teamExist(heldGame.greenTeam):
                        desc += "\r\nGreen team: " + str(heldGame.teamScore(heldGame.greenTeam, heldGame.greenBonus))
                        areTeams = True
                    if heldGame.teamExist(heldGame.orangeTeam):
                        desc += "\r\nOrange team: " + str(heldGame.teamScore(heldGame.orangeTeam, heldGame.orangeBonus))
                        areTeams = True
                    if heldGame.teamExist(heldGame.yellowTeam):
                        desc += "\r\nYellow team: " + str(heldGame.teamScore(heldGame.yellowTeam, heldGame.yellowBonus))
                        areTeams = True
                    if heldGame.teamExist(heldGame.purpleTeam):
                        desc += "\r\nPurple team: " + str(heldGame.teamScore(heldGame.purpleTeam, heldGame.purpleBonus))
                        areTeams = True
                    if areTeams:
                        desc += "\r\n\r\nIndividuals:"
                    
                emb = discord.Embed(title="Score", description=desc, color=0x57068C)
                for x,y in heldGame.scores.items():
                    if x.nick == None: # Tries to display the Member's Discord nickname if possible, but if none exists, displays their username.
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
                report = "Embedded score."
            else:
                report = "You need to start a game first! Use '!start' to start a game."
                await text.channel.send(report)
    
        if isBuzz(text.content):
            print("calling buzz")
            botSpoke = True
            if exist:
                # This block handles all team assignment that was done before the game started.
                red = get(text.guild.roles, name = 'Team red')
                if red in text.author.roles and not text.author in heldGame.redTeam:
                    heldGame.redTeam.append(text.author)
                    print("Added " + text.author.name +  " to red on buzz")
                blue = get(text.guild.roles, name = 'Team blue')
                if blue in text.author.roles and not text.author in heldGame.blueTeam:
                    heldGame.blueTeam.append(text.author)
                    print("Added " + text.author.name +  " to blue on buzz")
                green = get(text.guild.roles, name = 'Team green')
                if green in text.author.roles and not text.author in heldGame.greenTeam:
                    heldGame.greenTeam.append(text.author)
                    print("Added " + text.author.name +  " to green on buzz")
                orange = get(text.guild.roles, name = 'Team orange')
                if orange in text.author.roles and not text.author in heldGame.orangeTeam:
                    heldGame.orangeTeam.append(text.author)
                    print("Added " + text.author.name +  " to orange on buzz")
                yellow = get(text.guild.roles, name = 'Team yellow')
                if yellow in text.author.roles and not text.author in heldGame.yellowTeam:
                    heldGame.yellowTeam.append(text.author)
                    print("Added " + text.author.name +  " to yellow on buzz")
                purple = get(text.guild.roles, name = 'Team purple')
                if purple in text.author.roles and not text.author in heldGame.purpleTeam:
                    heldGame.purpleTeam.append(text.author)
                    print("Added " + text.author.name +  " to purple on buzz")
                
                if heldGame.bonusMode == False:
                    if heldGame.hasBuzzed(text.author):
                        print("You have already buzzed, " + text.author.mention + ".")
                    else:
                        if heldGame.canBuzz(text.author):
                            if len(heldGame.buzzes) < 1:
                                heldGame.buzz(text.author)
                                print("Buzzed!")
                                report = text.author.mention + " buzzed. Pinging reader: " + str(heldGame.reader.mention)
                                await text.channel.send(report)
                            else:
                                heldGame.buzz(text.author)
                                print("Buzzed!")
                                # because I don't want the bot to say anything if you buzz when someone has been recognized, each conditional needs its own await send.
                        else: # Might want to remove this if it causes too much clutter.
                            report = "Your team is locked out of buzzing, " + text.author.mention + "."
                            await text.channel.send(report)
                else:
                    report = "We are currently playing a bonus. You cannot buzz, " + text.author.mention + "."
                    await text.channel.send(report)
            else:
                report = "You need to start a game first! Use '!start' to start a game."
                await text.channel.send(report)
    
        if text.content.startswith('!github'):
            print("calling github")
            #gitImage = discord.File("templates/github.png", filename="templates/github.png")
            botSpoke = True
            emb = discord.Embed(title = "Lev's Quizbowl Bot", description = "", color = 0x57068C)
            #await text.channel.send("https://github.com/LevBernstein/LevQuizbowlBot")
            emb.add_field(name = "View this bot's source code at:", value = "https://github.com/LevBernstein/LevQuizbowlBot", inline = True)
            await text.channel.send(embed = emb)
            report = "Embedded github."
            
        if text.content.startswith('!report'):
            print("calling report")
            botSpoke = True
            emb = discord.Embed(title = "Report bugs or suggest features", description = "", color = 0x57068C)
            #await text.channel.send("Report any issues at:\r\nhttps://github.com/LevBernstein/LevQuizbowlBot/issues")
            emb.add_field(name = "Report any issues at:", value = "https://github.com/LevBernstein/LevQuizbowlBot/issues", inline = True)
            await text.channel.send(embed = emb)
            report = "Embedded report."
    
        if text.content.startswith('!help') or text.content.startswith('!commands') or text.content.startswith('!tutorial'):
            print("calling tutorial")
            emb = discord.Embed(title="Lev's Quizbowl Bot Commands", description="", color=0x57068C)
            emb.add_field(name= "!setup", value= "Run this once, after the bot first joins the server.", inline=True)
            emb.add_field(name= "!start", value= "Starts a new game.", inline=True)
            emb.add_field(name= "buzz", value= "Buzzes in.", inline=True)
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
            emb.add_field(name= "!undo", value= "Undoes the last score change.", inline=True) # DEPRECATED until I figure out the issue with TUnum tracking.
            emb.add_field(name= "!end", value= "Ends the active game.", inline=True)
            emb.add_field(name= "!tutorial", value= "Shows you this list.", inline=True)
            #emb.add_field(name= "_ _", value= "_ _", inline=True) # filler for formatting
            await text.channel.send(embed=emb)
            report = "Embedded tutorial."
            
        elif text.content.startswith('!tu'): # elif because otherwise !tutorial calls this too
            print("calling tu")
            if exist:
                report = "Current TU: #" + str(heldGame.TUnum + 1) + "."
            else:
                report = "You need to start a game first! Use '!start' to start a game."
            await text.channel.send(report)

        if text.content.startswith('!export'): # DEPRECATED will autoexport when !end is run
            """ The score will be automatically exported to a CSV file on your local machine.
            What the !export command will do, when implemented, is write that to a Google Sheet and send that to the server.
            TODO export score to CSV. Requires tracking score for each TU and switching bonuses to a binary system a la online scoresheets made by Ophir."""
            if exist:
                exportedTime = str(datetime.now())[:-5]
                emb = discord.Embed(title="Exported scoresheet at " + exportedTime + ".", description="", color=0x57068C)
                emb.add_field(name = "This feature has not been implemented yet!", value= "Make sure to check https://github.com/LevBernstein/LevQuizbowlBot for updates!", inline=False)
                await text.channel.send(embed=emb)
                report = "Embedded export."
            else:
                report = "You need to start a game first! Use '!start' to start a game."
                await text.channel.send(report)
        
        if exist and generateLogs:
            """Saves output of valid commands in the log file.
            To disable logging, set generateLogs to False in the setup at the top of this file.
            """
            newline = ( f'{str(datetime.now())[:-5]: <23}' + " " + f'{(text.author.name + ":"): >33}' + " " +  text.content + "\r\n")
            with open(heldGame.logFile, "a") as f:
                f.write(newline)
                if botSpoke:
                    newline = (f'{str(datetime.now())[:-5]: <23}' + " " + f'{"BOT: ": >34}' + report + "\r\n")
                    f.write(newline)
        
client.run(token)
