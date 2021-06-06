# Default modules:
import copy
import csv
from collections import deque
from datetime import datetime
#import pickle
#import os.path

# Installed modules:
import discord
import pandas as pd
from discord.ext import commands
from discord.utils import get
#from googleapiclient.discovery import build
#from google_auth_oauthlib.flow import InstalledAppFlow
#from google.auth.transport.requests import Request


#############################################################
# Backup(self, prev)
# This class is a backup of previous scores, for the purpose of being able to undo an incorrect points assignment.
# It is essentially a singly linked list with some additional data fields.
# Parameters: prev is the previous backup of the scores.
# Local variables that require explaining:
#   line: a backup of the previous bottom line of the scoresheet.
# Will be used starting in Version 1.9.X.
class Backup:
    def __init__(self, prev):
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
        self.line = ""

#############################################################
# Instance(self, channel, discordChannel)
# This class is an instance of an active game of Quizbowl.
# Every channel in which a game is run gets its own instance.
# You cannot have more than one Instance per channel.
# Parameters:
#   channel is the id of the Discord channel in which the instance is run.
#   discordChannel is the Discord channel object of the channel in which the instance is run.
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
#   lastTossupPoints: Used for giving bonus points to the individual when playing without teams.
#   lastNeg: Boolean that tracks whether the last buzz was a 0/-5. Used in undo.
#   oldScores: A Backup() of a given Instance's scores.
class Instance: # instance of an active game. Each channel a game is run in gets its own instance. You cannot have more than one game per channel.
    def __init__(self, channel, discordChannel):
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
        self.redRole = get(discordChannel.guild.roles, name = 'Team red')
        self.blueRole = get(discordChannel.guild.roles, name = 'Team blue')
        self.greenRole = get(discordChannel.guild.roles, name = 'Team green')
        self.orangeRole = get(discordChannel.guild.roles, name = 'Team orange')
        self.yellowRole = get(discordChannel.guild.roles, name = 'Team yellow')
        self.purpleRole = get(discordChannel.guild.roles, name = 'Team purple')
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
        self.logFile = ("gamelogs/" + str(self.getChannel())[-5:] + "-" + datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".log")
        self.csvScore = ("gamelogs/" + str(self.getChannel())[-5:] + "-" + datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".csv")
        # log and scoresheet filename format: channelID-YYYY-mm-DD-HH-MM-SS
        self.lastTossupPoints = 0
        # Used starting in Version 1.9.X:
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
        return mem in self.buzzed
    
    def clear(self):
        """Clears the buzzes and buzzed arrays, allowing all players to buzz in once more."""
        print("Clearing...")
        self.buzzes = deque()
        self.buzzed = deque()
        self.unlock()
        self.active = False
    
    def dead(self):
        """Marks a Tossup as dead, clears the buzzes and buzzed arrays, and advances TUnum."""
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
        self.TUnum += 1
    
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
        Having personally negged, or a teammate having negged. canBuzz() checks if a teammate has negged, 
        while hasBuzzed() checks if you, personally, have negged.
        """
        conditions = (
            (mem in self.redTeam and self.redNeg == True),
            (mem in self.blueTeam and self.blueNeg == True),
            (mem in self.greenTeam and self.greenNeg == True),
            (mem in self.orangeTeam and self.orangeNeg == True),
            (mem in self.yellowTeam and self.yellowNeg == True),
            (mem in self.purpleTeam and self.purpleNeg == True)
        )
        return not any(conditions)
    
    def inTeam(self, mem):
        """When bonus mode is enabled, this method reports the team of the buzzer."""
        if mem in self.redTeam:
            return self.redRole
        if mem in self.blueTeam:
            return self.blueRole
        if mem in self.greenTeam:
            return self.greenRole
        if mem in self.orangeTeam:
            return self.orangeRole
        if mem in self.yellowTeam:
            return self.yellowRole
        if mem in self.purpleTeam:
            return self.purpleRole
        return None
    
    def teamScore(self, team, teamBonus):
        """Returns a team's total score, including bonus points."""
        total = teamBonus
        for mem in team:
            if mem in self.scores:
                total += self.scores[mem]
        return total
    
    def teamExist(self, team):
        """Checks if a given team has members"""
        return len(team) > 0
    
    """
    def undo(self):
        # Reverts scores back to one tossup ago. Currently has major problems; see Issue #7 on the GitHub Issues page.
        self.scores = copy.copy(self.oldScores.scores)
        self.redBonus = self.oldScores.redBonus
        self.blueBonus = self.oldScores.blueBonus
        self.greenBonus = self.oldScores.greenBonus
        self.orangeBonus = self.oldScores.orangeBonus
        self.yellowBonus = self.oldScores.yellowBonus
        self.purpleBonus = self.oldScores.purpleBonus
        self.oldScores = self.oldScores.prev
        self.TUnum = self.oldScores.TUnum
        if self.lastNeg:
            self.TUnum += 1
            self.oldScores.TUnum += 1
        self.lastNeg = self.oldScores.lastNeg
        self.clear()
    """
    
    def gain(self, points):
        """Awards points to the player at the front of the buzzes queue. 
        If the points awarded is a positive number, they have gotten a TU correct, so it moves on to a bonus if those are enabled. Returns true.
        If the points awarded is a negative number or 0, they have gotten a TU incorrect, so it adds that to the individual's score and does not advance TUnum. Returns false.
        Rarely, a pickling error arises with the backup system; might have fixed by switching to copy from deepcopy.
        """
        awarded = False
        if self.active == True:
            self.lastTossupPoints = points
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
                    #with open(self.csvScore, "r") as f:
                        #body = f.readlines()
                    #print("Body 0 = " + body[0])
                    #lane = body[0]
                    #test = lane.split(",")
                    #if mem.name not in test:
                        #newLane = "TU#,Red Bonus,Blue Bonus,Green Bonus,Orange Bonus,Yellow Bonus,Purple Bonus,"
                        #for x,y in self.scores.items():
                            #newLane += x.name + ","
                        #newLane += mem.name + ",\r\n"
                        #print("New Body 0 = " + newLane)
                        #body = ''.join([i for i in body]).replace(lane, newLane)
                        #print(body)
                        #with open(self.csvScore, "w") as f:
                            #f.writelines(body)
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
                    #with open(self.csvScore, "r") as f:
                        #body = f.readlines()
                    #print("Body 0 = " + body[0])
                    #lane = body[0]
                    #test = lane.split(",")
                    #if mem.name not in test:
                        #newLane = "TU#,Red Bonus,Blue Bonus,Green Bonus,Orange Bonus,Yellow Bonus,Purple Bonus,"
                        #for x,y in self.scores.items():
                            #newLane += x.name + ","
                        #newLane += mem.name + ",\r\n"
                        #print("New Body 0 = " + newLane)
                        #body = ''.join([i for i in body]).replace(lane, newLane)
                        #print(body)
                        #with open(self.csvScore, "w") as f:
                            #f.writelines(body)
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
            #with open(self.csvScore) as f:
                #body = f.readlines()
                #subMems = body[0].split(',')
                #found = False
                #for i in range(len(subMems)):
                    #if mem.name == subMems[i]:
                        #spot = i
                        #found = True
                        #break
            #if found:
                #if self.oldScores.lastNeg: # if there has already been a neg on the current TU:
                    #with open(self.csvScore, "r") as f : # split the last line; replace spot with points
                        #reader = csv.reader(f, delimiter = ',')
                        #count = 0
                        #for row in reader:
                            #count += 1
                    #print(count)
                    #try:
                        #oldLane = body[count]
                        #newLane = body[count].split(',')
                        #print(newLane)
                        #print("New line length: " + str(len(newLane)))
                        #newLane[spot] = str(points)
                        #total = ""
                        #for item in newLane:
                            #total += item + ","
                        #body = ''.join([i for i in body]).replace(oldLane, total)
                        #with open(self.csvScore, "w") as f:
                            #f.writelines(body)
                    #except IndexError as err: # TODO fix indexerror that pops up from time to time
                        #print("IndexError!")
                        #print(err)
                #else:
                    #newLine = [str(self.TUnum + 1)]
                    #for i in range(6):
                        #newLine.append('0')
                    #for i in range (spot-7):
                        #newLine.append('')
                    #newLine.append(str(points))
                    #print(newLine)
                    #with open(self.csvScore, "a+", newline='') as f:
                        #writer = csv.writer(f)
                        #writer.writerow(newLine)
        if awarded:
            self.TUnum += 1 # If a positive # of points has been assigned, that means someone got the TU correct. Advance the TU count.
        return awarded

    def bonusGain(self, points):
        """Awards bonus points, either to the team or to the individual if playing without teams."""
        if not self.bonusEnabled or not self.bonusMode:
            return
        temp = copy.copy(self.oldScores)
        changed = -1
        if any(self.lastBonusMem in t for t in [self.redTeam, self.blueTeam, self.greenTeam, self.orangeTeam, self.yellowTeam, self.purpleTeam]):
            if self.lastBonusMem in self.redTeam:
                self.redBonus += points
                changed = 0
            elif self.lastBonusMem in self.blueTeam:
                self.blueBonus += points
                changed = 1
            elif self.lastBonusMem in self.greenTeam:
                self.greenBonus += points
                changed = 2
            elif self.lastBonusMem in self.orangeTeam:
                self.orangeBonus += points
                changed = 3
            elif self.lastBonusMem in self.yellowTeam:
                self.yellowBonus += points
                changed = 4
            elif self.lastBonusMem in self.purpleTeam:
                self.purpleBonus += points
                changed = 5
        else:
            self.scores[self.lastBonusMem] += points
        #with open(self.csvScore, "r+") as f:
            #body = f.readlines()
            #lastLine = body.pop().split(',')
        #with open(self.csvScore, "w") as f:
            #f.writelines(body)
        #print(lastLine)
        #lastLine[1] = "0"
        #lastLine[2] = "0"
        #lastLine[3] = "0"
        #lastLine[4] = "0"
        #lastLine[5] = "0"
        #lastLine[6] = "0"
        #searching = True
        #if changed != -1:
            #if searching and changed == 0:
                #lastLine[1] = str(points)
                #searching = False
            #if searching and changed == 1:
                #lastLine[2] = str(points)
                #searching = False
            #if searching and changed == 2:
                #lastLine[3] = str(points)
                #searching = False
            #if searching and changed == 3:
                #lastLine[4] = str(points)
                #searching = False
            #if searching and changed == 4:
                #lastLine[5] = str(points)
                #searching = False
            #if searching and changed == 5:
                #lastLine[6] = str(points)
        #else:
            #print("selfAdded")
            #found = False
            #with open(self.csvScore) as f:
                #body = f.readlines()
                #subMems = body[0].split(',')
                #found = False
                #for i in range(len(subMems)):
                    #if self.lastBonusMem.name == subMems[i]:
                        #spot = i
                        #found = True
                        #break
            #if found:
                #print("found")
                #print(self.lastTossupPoints)
                #print(points)
                #lastLine[spot] = str(self.lastTossupPoints + points)
                #print(lastLine[spot])
        #with open(self.csvScore, "a+", newline='') as f:
            #writer = csv.writer(f)
            #print(lastLine)
            #writer.writerow(lastLine)
        self.bonusMode = False
        
    def bonusStop(self):
        """Kills an active bonus."""
        if self.bonusEnabled:
            self.lastBonusMem = None
            self.bonusMode = False
        else:
            print("Could not stop a bonus!")