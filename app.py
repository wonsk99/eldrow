## Wordle clone for Discord
import random
import discord
import os
from dotenv import load_dotenv

from src.models.board import Board

# Read in token from env
load_dotenv()
token = os.getenv("TOKEN")

# Connect to Discord
client = discord.Client(intents=discord.Intents.all())

# Globals
GAMERS = {}
MAIN_SERVER_ID = 866838236658794507
MAIN_GUILD = discord.Object(id=MAIN_SERVER_ID)
servers = [866838236658794507, 800914273781022761, 946143984340836353, 711077719944724541] # Mine, Mine, Ours, Friends
GUILDS = [discord.Object(id=server) for server in servers]

# COMMANDS
tree = discord.app_commands.CommandTree(client)
@tree.command(name="start", description="Start a new game of Wordle", guild=MAIN_GUILD)
async def start(interaction: discord.Interaction):
    gamer = interaction.user
    if gamer in GAMERS:
        board = GAMERS[gamer]
        board.footer = "You already have a running game. Use /guess to proceed"
    else:
        board = Board(gamer)
        board.footer = "Welcome to Wordle"
        GAMERS[gamer] = board

    await board.start_game(interaction)

@tree.command(name="guess", description="Guess your next Word", guild=MAIN_GUILD)
async def guess(interaction: discord.Interaction, word: str):
    gamer = interaction.user

    if gamer not in GAMERS:
        board = Board(gamer)
        GAMERS[gamer] = board
    else:
        board = GAMERS[gamer]

    finito = await board.guess_word(interaction, word.upper().strip())

    if finito:
        del GAMERS[gamer]

# @tree.command(name="stats", description="View your stats", guild=MAIN_GUILD)
# async def stats(interaction: discord.Interaction):
#     await interaction.response.send_message("Stats for " + interaction.user.mention)

# @tree.command(name="mode", description="Swap to easy/hard", guild=MAIN_GUILD)
# async def stats(interaction: discord.Interaction, mode: str):
#     await interaction.response.send_message("Stats for " + interaction.user.mention)

import json
async def convert_emoji():
    raw_emojis = await client.fetch_application_emojis()

    tiles = {}

    for emoji in raw_emojis:
        tiles[emoji.name] = f"<:{emoji.name}:{emoji.id}>"

    with open("data/emoji_dict.json", "w") as f:
        json.dump(tiles, f, indent=4)

    f.close()

# When bot logs in
@client.event
async def on_ready():
    await convert_emoji()
    print('Logged in as {0.user}'.format(client))

    # Main guild syncs
    for guild in GUILDS:
        syncd = await tree.sync(guild=guild)
        print(syncd)

    # Global sync
    await tree.sync()

if __name__ == "__main__":
    client.run(token)