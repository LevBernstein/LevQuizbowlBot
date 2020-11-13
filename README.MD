# Lev's Quizbowl Bot

A Discord bot designed for playing Quizbowl,
written in Python.

Originally created for use in the Quiz Bowl at NYU Discord server. 

## Installation

1. Download the repository.

2. Create a file named "token.txt" that contains your Discord API token.

3. Place token.txt in the same folder as QBBot.py.

Alternatively, if you just want to add the bot to your own Discord 
server while I host it, you can simply click this link: 
https://discord.com/api/oauth2/authorize?client_id=776233398954885140&permissions=8&scope=bot

I'll hopefully have the bot online most of the time, but just in case I'm offline, hosting it
yourself is a good idea.

### Dependencies

* Python 3. To install, visit https://python.org/downloads/ and follow the instructions for your OS.

* Discord.py. To install, run "python3 -m pip install -U discord.py"

### Setup

You will have to make a role named "reader" that is lower in the role hierarchy than the bot's highest role.

If you want to make use of teams, you will need to make the following roles:

* Team red

* Team blue

* Team green

* Team orange

* Team yellow

* Team purple

All of them must be lower in the role hierarchy than the bot's highest role.


### Running the bot

In the Unix command line, cd to the directory containing QBBot.py. Then run "python3 QBBot.py"

## To-Do

* Teams. Will be done with roles.

* Proper handling of bonuses. Currently, you can handle someone getting 10 on a TU and 20 on a bonus by giving them 30. This is a inelegant solution.

* Proper TU# tracking and reporting.

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
