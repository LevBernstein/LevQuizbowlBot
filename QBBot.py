# Lev's Quizbowl Bot
# Author: Lev Bernstein
# Version: 1.8.17
# This bot is designed to be a user-friendly Quizbowl Discord bot with a minimum of setup.
# All commands are documented; if you need any help understanding them, try the command !tutorial.
# This bot is free software, licensed under the GNU GPL version 3. If you want to modify the bot in any way,
# you are absolutely free to do so. If you make a change you think others would enjoy, I'd encourage you to
# make a pull request on the bot's GitHub page (https://github.com/LevBernstein/LevQuizbowlBot/tree/pandasRewrite).

# Default modules:
import asyncio
import copy
import csv
from collections import deque, OrderedDict
from datetime import datetime
from operator import itemgetter
from sys import exit as sysExit
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

# Custom modules:
from Summon import *
from Instance import *


# Setup
try:
    with open("token.txt", "r") as f: # in token.txt, paste in your own Discord API token
        token = f.readline()
except:
    print("Error! Could not read token.txt!")
    sysExit(-1)
    
generateLogs = True # if the log files are getting to be too much for you, set this to False. Scoresheet exporting will still work.
verbosePings = True
client = discord.Client()

# Global helper methods
def isInt(st):
    """Checks if an entered string would be a valid number of points to assign."""
    if len(st) == 0: # this conditional handles an issue with the bot trying to interpret attached images as strings
        return False
    if st.startswith('<:ten:') or st.startswith('<:neg:') or st.startswith('<:power:'): # this conditional handles awarding points with emojis
        return True
    return st[1:].isdigit() if (st[0] == '-' or st[0] == '+') else st.isdigit()

def isBuzz(st):
    """Checks if an entered string is a valid buzz. If you want to allow additional means of buzzing, add them to validBuzzes."""
    return any(st.startswith(string) for string in ['buz', '<:buzz:', 'bz', '!bz', '!buz', '<:bee:'])

def writeOut(generate, name, content, game, report, spoke):
    """Saves output of valid commands in the log file.
    To disable logging, set generateLogs to False in the setup at the top of this file.
    Generally passed: generate = generateLogs, name = text.author.name, content = text.content, game = heldGame, report = report, spoke = botSpoke
    So: writeOut(generateLogs, text.author.name, text.content, heldGame, report, botSpoke)
    """
    if generate:
        newline = (f'{str(datetime.now())[:-5]: <23}' + " " + f'{(name + ":"): >33}' + " " +  content + "\r\n")
        with open(game.logFile, "a") as f:
            f.write(newline)
            if spoke:
                newline = (f'{str(datetime.now())[:-5]: <23}' + " " + f'{"BOT: ": >34}' + report + "\r\n")
                f.write(newline)
    return


games = [] # List holding all active games across all channels and servers. If this bot sees sufficiently large usage, I will switch to something more sorted to store the games, like a BST or a 2-3 tree. Games would be sorted based on channel ID.


@client.event
async def on_ready():
    """Ready message for when the bot is online."""
    await client.change_presence(activity=discord.Game(name='Quiz Bowl!'))
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
    if not text.author.bot:
        for i in range(len(games)):
            if current == games[i].getChannel():
                exist = True
                print(str(current) + " " + str(datetime.now())[:-5] + " " + text.author.name + ": " + text.content) # I disabled printing every message because it was just too much. Now it only prints if a game is active.
                heldGame = games[i]
                break
        
        if text.content.startswith('!setup'):
            print("Running setup...")
            botSpoke = True
            """Run this command once, after you add the bot the your server. It will handle all role and emoji creation, and set the bot's avatar.
            Please avoid running this command more than once, as doing so will create duplicate emojis. If for whatever reason you have to do so, that's fine, just be prepared to delete those emojis.'
            """
            report = "This command is only usable by server admins!"
            if text.author.guild_permissions.administrator: # Bot setup requires admin perms.
                await text.channel.send("Starting setup...")
                report = "Successfully set up the bot!"
                
                # This block handles role creation. The bot requires these roles to function, so it will make them when you run !setup.
                willHoist = True # Hoist makes it so that a given role is displayed separately on the sidebar. If for some reason you don't want teams displayed separately, set this to False.
                roles = {
                    "Reader": 0x01ffdd,
                    "Team red": 0xf70a0a,
                    "Team blue": 0x009ef7,
                    "Team green": 0x7bf70b,
                    "Team orange": 0xff6000,
                    "Team yellow": 0xfeed0e,
                    "Team purple": 0xb40eed
                }
                for x, y in roles.items():
                    if not get(text.guild.roles, name = x):
                        await text.guild.create_role(name = x, colour = discord.Colour(y), hoist = willHoist)
                        print("Created " + x + ".")
                print("Roles live!")
                
                # This block creates the emojis the bot accepts for points and buzzes. Credit for these wonderful emojis goes to Theresa Nyowheoma, President of Quiz Bowl at NYU, 2020-2021.
                try:
                    with open("templates/emoji/buzz.png", "rb") as buzzIMG:
                        img = buzzIMG.read()
                        buzz = await text.guild.create_custom_emoji(name = 'buzz', image = img)
                    with open("templates/emoji/neg.png", "rb") as negIMG:
                        img = negIMG.read()
                        neg = await text.guild.create_custom_emoji(name = 'neg', image = img)
                    with open("templates/emoji/ten.png", "rb") as tenIMG:
                        img = tenIMG.read()
                        ten = await text.guild.create_custom_emoji(name = 'ten', image = img)
                    with open("templates/emoji/power.png", "rb") as powerIMG:
                        img = powerIMG.read()
                        power = await text.guild.create_custom_emoji(name = 'power', image = img)
                    print("Emoji live!")
                    report += " Team roles now exist, as do the following emoji: " + str(buzz) + ", " + str(neg) + ", " + str(ten) + ", " + str(power) + "."
                    with open("templates/pfp.png", "rb") as pfp:
                        pic = pfp.read()
                        try:
                            await client.user.edit(avatar=pic) # Running !setup too many times will cause the Discord API to deny API calls that try to change the profile picture.
                            print("Avatar live!")
                        except discord.HTTPException: # In case of the above issue:
                            print("Avatar failed to update!")
                            report += " Failed to update the Bot's profile picture."
                except FileNotFoundError:
                    report = "Failed to load images for emoji or profile picture! Check your directory structure."
    
            await text.channel.send(report)
            if exist:
                writeOut(generateLogs, text.author.name, text.content, heldGame, report, botSpoke)
            return
        
        if text.content.startswith('!summon') or text.content.startswith('!call'):
            """Mentions everyone in the server, pinging them and informing them that it is time for practice."""
            print("calling summon")
            botSpoke = True
            report = "This command is only usable by server admins!"
            if text.author.guild_permissions.administrator: # this makes sure people can't just ping everyone in the server whenever they want. Only admins can do that.
                report = summon() if verbosePings else "@everyone it's time for Quiz Bowl practice."# For the full list of summon messages, check Summon.py.
            await text.channel.send(report)
            if exist:
                writeOut(generateLogs, text.author.name, text.content, heldGame, report, botSpoke)
            return
    
        if text.content.startswith('!start') or text.content.startswith('!begin') or text.content.startswith('!read'):
            botSpoke = True
            print("calling start")
            if exist:
                report = "You already have an active game in this channel."
            else:
                role = get(text.guild.roles, name = 'Reader') # The bot needs you to make a role called "Reader" in order to function.
                if role:
                    report = "Starting a new game. Reader is " + text.author.mention + "."
                    x = Instance(current, text.channel)
                    x.reader = text.author
                    print(x.getChannel())
                    await text.author.add_roles(role)
                    heldGame = x
                    with open(x.logFile, "a") as f:
                        f.write("Start of game in channel " + str(current) + " at " + datetime.now().strftime("%H:%M:%S") + ".\r\n\r\n")
                    with open(x.csvScore, "a") as f:
                        #f.write("TU#,Red Bonus,Blue Bonus,Green Bonus,Orange Bonus,Yellow Bonus,Purple Bonus,")
                        # Currently creates the scoresheet and does nothing else.
                        pass
                    games.append(x)
                else:
                    report = "You need to run !setup before you can start a game."
            await text.channel.send(report)
            if exist:
                writeOut(generateLogs, text.author.name, text.content, heldGame, report, botSpoke)
            return
        
        if exist: # These commands only fire if a game is active in the channel in which they are being run.
            if text.content.startswith('!newreader'):
                print("calling newreader")
                botSpoke = True
                target = text.content.split('@', 1)[1]
                target = target[1:-1] if target.startswith('!') else target[:-1]
                role = get(text.guild.roles, name = 'Reader')
                await heldGame.reader.remove_roles(role)
                newReader = await text.guild.fetch_member(target)
                heldGame.reader = newReader
                await newReader.add_roles(role)
                report = "Made " + newReader.mention + " the new reader."
                await text.channel.send(report)
                writeOut(generateLogs, text.author.name, text.content, heldGame, report, botSpoke)
                return
            
            if text.content.startswith('!end') or text.content.startswith('!stop'):
                print("calling end")
                botSpoke = True
                for i in range(len(games)):
                    if current == games[i].getChannel():
                        if text.author.id == games[i].reader.id or text.author.guild_permissions.administrator:
                            #with open(games[i].csvScore) as f:
                                #body = f.readlines()
                                #subMems = body[0]
                            #newLine = "Total:," + str(games[i].redBonus) + "," + str(games[i].blueBonus) + "," + str(games[i].greenBonus) + "," + str(games[i].orangeBonus) + "," + str(games[i].yellowBonus) + "," + str(games[i].purpleBonus) + ","
                            #with open(games[i].csvScore, "a") as f:
                                #for x, y in games[i].scores.items():
                                    #newLine += str(y) + ","
                                #f.write(newLine)
                            csvName = games[i].csvScore
                            games.pop(i)
                            report = "Ended the game active in this channel. Here is the scoresheet (I am rewriting all the code involving the scoresheet; it will be extremely inaccurate for some time. Scoresheets are currently empty)."
                            #report = "Ended the game active in this channel."
                            role = get(text.guild.roles, name = 'Reader')
                            await heldGame.reader.remove_roles(role) # The Reader is stored as a Member object in heldGame, so any admin can end the game and the Reader role will be removed.
                            await text.channel.send(report)
                            await text.channel.send(file=discord.File(csvName, filename="scoresheet.csv"))
                        else:
                            report = "You are not the reader or a server admin!"
                            await text.channel.send(report)
                        break
                writeOut(generateLogs, text.author.name, text.content, heldGame, report, botSpoke)
                return

            """
            # DEPRECATED until I fully implement scoresheets and figure out the issue with TUnum tracking.
            if text.content.startswith('!undo'):
                print("calling undo")
                botSpoke = True
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
                writeOut(generateLogs, text.author.name, text.content, heldGame, report, botSpoke)
                return
            """
            
            if text.content.startswith('!dead'):
                print("calling dead")
                botSpoke = True
                report = "You are not the reader!"
                if text.author.id == heldGame.reader.id:
                    heldGame.dead()
                    report = "TU goes dead. Moving on to TU #" + str(heldGame.TUnum + 1) + "."
                await text.channel.send(report)
                writeOut(generateLogs, text.author.name, text.content, heldGame, report, botSpoke)
                return
            
            if text.content.startswith('!clear'):
                print("calling clear")
                botSpoke = True
                report = "You are not the reader!"
                if text.author.id == heldGame.reader.id:
                    heldGame.clear()
                    report = "Buzzers cleared, anyone can buzz." 
                await text.channel.send(report)
                writeOut(generateLogs, text.author.name, text.content, heldGame, report, botSpoke)
                return
            
            if isInt(text.content): # Assigns points.
                print("calling points")
                print(text.content + " is an int")
                if text.content.startswith('<:neg:'): # This and the next two conditionals check to see if someone is using a valid emoji to assign points. While, to the user, an emoji looks like :emojiName:, to the bot it is also wrapped in <>.
                    text.content = "-5"
                elif text.content.startswith('<:ten:'):
                    text.content = "10"
                elif text.content.startswith('<:power:'):
                    text.content = "15"
                botSpoke = True
                report = "Null" # if someone besides the reader types a number, this will do nothing
                if text.author.id == heldGame.reader.id:
                    if heldGame.bonusEnabled == False:
                        if heldGame.gain(int(text.content)):
                            report = "Awarded points. Moving on to TU #" + str(heldGame.TUnum + 1) + "."
                            await text.channel.send(report)
                        else:
                            report = "No held buzzes."
                            while len(heldGame.buzzes) > 0:
                                if heldGame.canBuzz(heldGame.buzzes[0]):
                                    report = (heldGame.buzzes[0]).mention + " buzzed. Pinging reader: " + str(heldGame.reader.mention)
                                    await text.channel.send(report)
                                    break
                                else:
                                    heldGame.buzzes.popleft() # Pop until we find someone who can buzz, or until the array of buzzes is empty.
                                    report = "Cannot buzz."
                    else: # bonuses enabled
                        if heldGame.bonusMode == False:
                            storedMem = heldGame.buzzes[0]
                            if heldGame.gain(int(text.content)):
                                report = "Awarded TU points. "
                                getTeam = heldGame.inTeam(storedMem)
                                message = await text.channel.send(report)
                                if getTeam != None:
                                    report += "Bonus is for " + getTeam.mention + ". "
                                report +=  "Awaiting bonus points."
                                await asyncio.sleep(.1)
                                await message.edit(content=report)
                            else:
                                report = "No held buzzes."
                                while len(heldGame.buzzes) > 0:
                                    if heldGame.canBuzz(heldGame.buzzes[0]):
                                        report = (heldGame.buzzes[0]).mention + " buzzed. Pinging reader: " + str(heldGame.reader.mention)
                                        await text.channel.send(report)
                                        break
                                    else:
                                        heldGame.buzzes.popleft() # Pop until we find someone who can buzz, or until the array of buzzes is empty.
                                        report = "Cannot buzz."
                                        # because I don't want to send a report here, I can't have the text.channel.send(report) at the end
                        else: # bonusMode true
                            heldGame.bonusGain(int(text.content))
                            report = "Awarded bonus points. Moving on to TU #" + str(heldGame.TUnum + 1) + "."
                            await text.channel.send(report)
                writeOut(generateLogs, text.author.name, text.content, heldGame, report, botSpoke)
                return
            
            if text.content.startswith('wd') or text.content.startswith('!wd') or text.content.startswith('withdraw') or text.content.startswith('!withdraw'):
                print("calling withdraw")
                botSpoke = True
                report = "Only the currently recognized player can withdraw."
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
                await text.channel.send(report)
                writeOut(generateLogs, text.author.name, text.content, heldGame, report, botSpoke)
                return
            
            if text.content.startswith('!bonusmode') or text.content.startswith('!btoggle'):
                """Toggles whether bonus mode is enabled. It is enabled by default."""
                print("calling bonusmode")
                botSpoke = True
                report = "You are not the reader!"
                if text.author.id == heldGame.reader.id or text.author.guild_permissions.administrator:
                    heldGame.bonusStop()
                    heldGame.bonusEnabled = not heldGame.bonusEnabled
                    report = "Enabled bonus mode." if heldGame.bonusEnabled else "Disabled bonus mode."
                await text.channel.send(report)
                writeOut(generateLogs, text.author.name, text.content, heldGame, report, botSpoke)
                return
            
            if text.content.startswith('!bstop'):
                """Ends current bonus round. Use this to kill a bonus without giving points. Only use if something has gone wrong and you need to kill a bonus immediately."""
                print("calling bstop")
                botSpoke = True
                report = "You are not the reader!"
                if text.author.id == heldGame.reader.id:
                    heldGame.bonusStop()
                    report = "Killed active bonus. Next TU."
                await text.channel.send(report)
                writeOut(generateLogs, text.author.name, text.content, heldGame, report, botSpoke)
                return
        
            if text.content.startswith('!score'):
                print("calling score")
                diction = {}
                botSpoke = True
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
                for x, y in heldGame.scores.items():
                    if x.nick == None: # Tries to display the Member's Discord nickname if possible, but if none exists, displays their username.
                        diction[x.name] = y
                    else:
                        diction[x.nick] = y
                sortedDict = OrderedDict(sorted(diction.items(), key = itemgetter(1)))
                print(sortedDict)
                for i in range(len(sortedDict.items())):
                    tup = sortedDict.popitem()
                    emb.add_field(name=(str(i+1) + ". " + tup[0]), value=str(tup[1]), inline=True)
                await text.channel.send(embed=emb)
                report = "Embedded score."
                writeOut(generateLogs, text.author.name, text.content, heldGame, report, botSpoke)
                return
        
            if isBuzz(text.content): # Uses the isBuzz() helper method to dermine if somene is buzzing
                print("calling buzz")
                botSpoke = True
                # This block handles all team assignment that was done before the game started.
                red = get(text.guild.roles, name = 'Team red')
                blue = get(text.guild.roles, name = 'Team blue')
                green = get(text.guild.roles, name = 'Team green')
                orange = get(text.guild.roles, name = 'Team orange')
                yellow = get(text.guild.roles, name = 'Team yellow')
                purple = get(text.guild.roles, name = 'Team purple')
                if red in text.author.roles and not text.author in heldGame.redTeam:
                    heldGame.redTeam.append(text.author)
                    print("Added " + text.author.name +  " to red on buzz")
                elif blue in text.author.roles and not text.author in heldGame.blueTeam:
                    heldGame.blueTeam.append(text.author)
                    print("Added " + text.author.name +  " to blue on buzz")
                elif green in text.author.roles and not text.author in heldGame.greenTeam:
                    heldGame.greenTeam.append(text.author)
                    print("Added " + text.author.name +  " to green on buzz")
                elif orange in text.author.roles and not text.author in heldGame.orangeTeam:
                    heldGame.orangeTeam.append(text.author)
                    print("Added " + text.author.name +  " to orange on buzz")
                elif yellow in text.author.roles and not text.author in heldGame.yellowTeam:
                    heldGame.yellowTeam.append(text.author)
                    print("Added " + text.author.name +  " to yellow on buzz")
                elif purple in text.author.roles and not text.author in heldGame.purpleTeam:
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
                                report = "Held a buzz."
                                print("Buzzed!")
                                # because I don't want the bot to say anything if you buzz when someone has been recognized, each conditional needs its own await send.
                        else:
                            report = "Your team is locked out of buzzing, " + text.author.mention + "."
                            await text.channel.send(report)
                else:
                    report = "We are currently playing a bonus. You cannot buzz, " + text.author.mention + "."
                    await text.channel.send(report)
                writeOut(generateLogs, text.author.name, text.content, heldGame, report, botSpoke)
                return
        
        if text.content.startswith('!github'):
            print("calling github")
            botSpoke = True
            emb = discord.Embed(title = "Lev's Quizbowl Bot", description = "", color = 0x57068C)
            emb.add_field(name = "View this bot's source code at:", value = "https://github.com/LevBernstein/LevQuizbowlBot/tree/pandasRewrite", inline = True)
            await text.channel.send(embed = emb)
            report = "Embedded github."
            if exist:
                writeOut(generateLogs, text.author.name, text.content, heldGame, report, botSpoke)
            return
            
        if text.content.startswith('!report'):
            print("calling report")
            botSpoke = True
            emb = discord.Embed(title = "Report bugs or suggest features", description = "", color = 0x57068C)
            emb.add_field(name = "Report any issues at:", value = "https://github.com/LevBernstein/LevQuizbowlBot/issues", inline = True)
            await text.channel.send(embed = emb)
            report = "Embedded report."
            if exist:
                writeOut(generateLogs, text.author.name, text.content, heldGame, report, botSpoke)
            return
    
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
            emb.add_field(name= "!call", value= "Mentions everyone in the server and informs them that it is time for practice. Usable only by admins.", inline=True)
            emb.add_field(name= "!github", value= "Gives you a link to this bot's github page.", inline=True)
            emb.add_field(name= "!report", value= "Gives you a link to this bot's issue-reporting page.", inline=True)
            emb.add_field(name= "!tu", value= "Reports the current tossup number.", inline=True)
            emb.add_field(name= "!team [red/blue/green/orange/yellow/purple]", value= "Assigns you the team role corresponding to the color you entered.", inline=True)
            emb.add_field(name= "!bonusmode", value= "Disables or enables bonuses. Bonuses are enabled by default.", inline=True)
            emb.add_field(name= "!bstop", value= "Kills an active bonus without giving points.", inline=True)
            emb.add_field(name= "!newreader <@user>", value= "Changes a game's reader to another user.", inline=True)
            emb.add_field(name= "wd", value= "Withdraws a buzz.", inline=True)
            # emb.add_field(name= "!undo", value= "Reverts the last score change.", inline=True) # DEPRECATED until I figure out the issue with TUnum tracking.
            emb.add_field(name= "!end", value= "Ends the active game.", inline=True)
            emb.add_field(name= "!tutorial", value= "Shows you this list.", inline=True)
            #emb.add_field(name= "_ _", value= "_ _", inline=True) # filler for formatting
            await text.channel.send(embed=emb)
            report = "Embedded commands list."
            if exist:
                writeOut(generateLogs, text.author.name, text.content, heldGame, report, botSpoke)
            return
            
        if exist and text.content.startswith('!tu'): # Placed after !help so that it won't fire when someone does !tutorial, a synonym of !help
            print("calling tu")
            report = "Current TU: #" + str(heldGame.TUnum + 1) + "."
            await text.channel.send(report)
            writeOut(generateLogs, text.author.name, text.content, heldGame, report, botSpoke)
            return
        
        if text.content.startswith('!team'):
            """ Adds the user to a given team.
            Teams require the following roles: Team red, Team blue, Team green, Team orange, Team yellow, Team purple.
            If you do not have those roles in your server, the bot will create them for you when you run !setup. 
            Depending on your role hierarchy, the bot-created roles might not show their color for each user.
            Make sure that, for non-admin users, the team roles are the highest they can have in the hierarchy.
            Admin roles should still be higher than the team roles.
            """
            print("calling team")
            botSpoke = True
            rolesExist = False
            rolesFound = False
            roles = ["red", "blue", "green", "orange", "yellow", "purple"]
            for role in roles:
                if text.content.startswith('!team ' + role):
                    rolesFound = True
                    givenRole = get(text.guild.roles, name = 'Team ' + role)
                    if givenRole:
                        await text.author.add_roles(givenRole)
                        report = "Gave you the Team " + role + " role, " + text.author.mention + "."
                        rolesExist = True
                        break
            if not rolesExist:
                report = "Uh-oh! The Discord role you are trying to add does not exist! If whoever is going to read does !start, I will create the roles for you."
            if not rolesFound:
                report = "Please choose a valid team! Valid teams are red, blue, green, orange, yellow, and purple."
            await text.channel.send(report)
            if exist:
                writeOut(generateLogs, text.author.name, text.content, heldGame, report, botSpoke)
            return
       
client.run(token)
