# Lev's Quizbowl Bot

Stable Build: [Release 1.7.2](https://github.com/LevBernstein/LevQuizbowlBot/releases/tag/v1.7.2)

Unstable Build: Release 1.8.3

A Discord bot designed for playing Quizbowl, written in Python.

Originally created for use in the Quiz Bowl at NYU Discord server.

This bot keeps track of all the boring stuff, allowing you to focus on reading and buzzing. Designed for use in Quizbowl practices over Discord, all you need is a reader and you're good to go.

## Installation

1. Download the repository.

2. Create a file named "token.txt" that contains your Discord API token.

3. Place token.txt in the same folder as QBBot.py.

Alternatively, if you just want to add the bot to your own Discord 
server while I host it, [you can simply click this link](https://discord.com/api/oauth2/authorize?client_id=776233398954885140&permissions=8&scope=bot).

I'll hopefully have the bot online most of the time, but just in case I'm offline, hosting it
yourself is a good idea.

### Dependencies

* Python 3. To install, visit [the Python downloads page](https://python.org/downloads/) and follow the instructions for your OS.

* Discord.py. To install, run "python3 -m pip install -U discord.py"

* Pandas. To install, run "pip install pandas"

* Future versions will require the Google Client Library; this version does not. To install it, run "pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib"

### Setup

After adding the bot to your server, run the command !setup (only users with the "Administrator" permission can use this command). This will create the required roles and emojis.

The bot requires the existence of a reader role and team roles; it will create those for you when you run !setup.
Newly created roles are, by default, lowest in the role hierarchy; if you want to make everyone display their team color, make sure the team roles the bot uses
are higher in the role hierarchy than whatever other non-admin roles are giving people their color.

In addition to giving points by entering numbers, the bot allows you to give points through Discord emojis.
These emojis must have the names :neg:, :power:, and :ten:. You can also buzz with :buzz:.
The bot will create these emojis for you when you run !setup.
Provided in "templates/emoji" are images used for those emotes in the NYU QB server, as created by Theresa Nyowheoma.
The bot will use those images for the emojis, but you can also replace them with images of your own, if you so desire.
You will still be able to buzz with those emojis if you change the images, so long as their names are still neg, power, and ten.

### Running the bot

In the *nix command line, cd to the directory containing QBBot.py. Then run "python3 QBBot.py"

The bot outputs a lot to the command line, just because I like having a lot of information available.
You can comment out the print statements if they annoy you.
In addition, the bot creates a new log file for each game (and a .csv scoresheet [WIP]).
If you want to disable log file generation, set generateLogs to False in the Setup section of QBBot.py (~Line 36).

## To-Do

* Undo command. Implemented in version 1.5.14; deprecated in version 1.6.3. Needs fixes.

* Automatically export scoresheets to Google Sheets.

* Score exporting through .csv files. Beta version implemented in version 1.6.6; temporarily disabled in public release 1.6.8. In progress in versions >= 1.7.3.

* <strike>Targeted new reader command.</strike> Implemented in version 1.7.0.

* <strike>Autocreate required roles and emojis.</strike> Implemented in version 1.5.4.

* <strike>Command that sets a new reader.</strike> Implemented in version 1.4.6.

* <strike>Record logs for each game.</strike> Implemented in version 1.5.0.

* <strike>Allow emoji for points/buzzing.</strike> Implemented in version 1.4.3.

* <strike>Teams.</strike> Implemented in version 1.4.0.

* <strike>Bonuses.</strike> Implemented in version 1.3.0.

* <strike>Tossup number tracking.</strike> Implemented in version 1.2.1.

## License
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
