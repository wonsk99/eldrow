#!/usr/bin/env python3

## Wordle clone for Discord
import random
import discord as disc
import os
from dotenv import load_dotenv

# Read in token from env
load_dotenv()
token = os.getenv("TOKEN")

## FUNCTIONS##

# Initialize game
def initGame(gamer):
	games[gamer] = {}
	games[gamer]["Msg"] = ""
	games[gamer]["toDel"] = []
	games[gamer]["turn"] = 1
	games[gamer]["guesses"] = [[]]*6
	games[gamer]["answer"] = genWord()
	games[gamer]["rems"] = setrem(games[gamer]["answer"])
	games[gamer]["Greens"] = set()
	games[gamer]["Yellows"] = set()
	games[gamer]["Grays"] = set()
	games[gamer]["State"] = False
	games[gamer]["footer"] = ""

	return

# Generate a random word to guess
def genWord():
	ans = LISTED[random.randint(0,len(LISTED))].strip().upper()
	print(ans)
	return ans

# Set remaining letters
def setrem(target):
	rem = {}
	for l in target:
		if l not in rem:
			rem[l] = 0
		rem[l] += 1
	return rem

# Delete a message
def delM(gamer, m):
	if isinstance(m, disc.message.Message):
		games[gamer]["toDel"].append(m)
	return

# Format letter
def color(l, fmt):
	return(fmt + l + fmt)
	

# Print keyboard
def dispKeys(gamer):
	kRow = ""
	for key in KEYS:
		for l in key:
			if l in games[gamer]["Greens"]:
				p = color(l, Format.B)
			elif l in games[gamer]["Yellows"]:
				p = color(l, Format.U)
			elif l in games[gamer]["Grays"]:
				p = color(l, Format.S)
			else:
				p = color(l, Format.I)
			kRow += p
			kRow += " "
		kRow += "\n"
	return kRow

# Print board
def dispBoard(gamer):
	# Guesses
	tWho = "{}'s guesses:\n".format(gamer[0].mention)

	# BOARD
	ct = 1
	tBoard = ""
	for row in games[gamer]["guesses"]:
		tRow = "{}. ".format(str(ct))
		for letter in row:
			tRow += letter
			tRow += " "
		ct += 1
		tRow += "\n"
		tBoard += tRow
	return tWho + tBoard + "\n"

# Print function
def printGame(gamer):
	tUser = "{}'s game".format(gamer[0].display_name)
	tBoard = dispBoard(gamer)
	tKeys = dispKeys(gamer)
	
	# Create embed
	e = disc.Embed(title=tUser, description=tBoard+tKeys, color=0x00ff00)
	e.set_footer(text=games[gamer]["footer"])
	return e

# Check if letter is in word
def checkr(letter, rem):
	rem[letter] -= 1
	if rem[letter] == 0:
		del rem[letter]
	return rem

# Check for valid guess
def checkvalid(guess):
	# Check len
	guess = guess.strip().lower()
	if len(guess) != 5:
		return False

	# In the dictionary
	if guess in FULL:
		return True
	return False

# THE ACTUAL GAME
def eLogic(gamer, guess):
	gDict = games[gamer]
	rem = dict(gDict["rems"])

	word = list(guess.upper())
	unchecked = set([0,1,2,3,4])

	# Green
	for i in range(0,5):
		if word[i] == gDict["answer"][i]:
			rem = checkr(word[i], rem)
			gDict["Greens"].add(word[i])
			word[i] = color(word[i], Format.B)
			unchecked.remove(i)

	if len(rem) <= 0:
		gDict["guesses"][gDict["turn"]-1] = word
		gDict["State"] = True

	# Yellow
	for i in range(0,5):
		if word[i] in rem:
			rem = checkr(word[i], rem)
			if word[i] not in gDict["Greens"]:
				gDict["Yellows"].add(word[i])
			word[i] = color(word[i], Format.U)
			unchecked.remove(i)

	# Gray
	for i in unchecked:
		if word[i] not in gDict["Greens"]:
			gDict["Grays"].add(word[i])
		word[i] = color(word[i], Format.S)

	gDict["guesses"][gDict["turn"]-1] = word

	return

## End FUNCTIONS ##

# Class to organize text formatting
class Format:
	B = "**"
	U = "__"
	S = "~~"
	I = "*"

## Disc Client ##

# Args
eArgs =	'''
Commands:
			-eldr start
			-eldr g <WORD>
			-eldr oops (Use this when the game disappears from your screen)

Keys:
			**Bolds** are right word in the right spot
			__Underlines__ are in the word in the wrong spot
			~~Strikethroughs~~ are not in the word
'''
# Create embed
eAmbed = disc.Embed(title="Rules", description=eArgs, color=0xff002b)

## GLOBALS ##
# Running Games
games = {}

# Running Rules
rules = {}

# List
DICT = "complete.txt"
# For ease of indexing
FULL = set()
# For sake of randomizing
LISTED = []
with open(DICT) as f:
	for word in f.readlines():
		LISTED.append(word.strip())
		FULL.add(word.strip())

# Keyboard stuff
KEYS = []
KEYS.append(list("QWERTYUIOP"))
KEYS.append(list("ASDFGHJKL"))
KEYS.append(list("ZXCVBNM"))

## END GLOBALS ##

# Connect to Discord
client = disc.Client()

# When bot logs in
@client.event
async def on_ready():
	print('Logged in as {0.user}'.format(client))

# When message receive
@client.event
async def on_message(message):
	gamer = (message.author, message.guild, message.channel)
	gwhere = (message.guild, message.channel)
	# Ignore messages from bot itself
	if gamer[0] == client.user:
		return
	
	# Receive message that begins with eldrow
	if message.content.startswith('-eldr'):
		# Parse message
		mText = message.content.split()

		if mText[0] != "-eldr":
			return

		if len(mText) < 2:
			if gamer in games:
				# TODO Delete "-eldr"
				delM(gamer, message)
				delM(gamer, games[gamer]["Msg"])

				games[gamer]["footer"] = "Review the rules below!"
				content = printGame(gamer)
				games[gamer]["Msg"] = await message.channel.send(embed=content)
				games[gamer]["footer"] = ""

				for allMsg in games[gamer]["toDel"]:
					await allMsg.delete()
				games[gamer]["toDel"] = []

			emsg = await message.channel.send(embed=eAmbed)
			if gwhere in rules:
				await rules[gwhere].delete()
			rules[gwhere] = emsg

			return
		# Game Start
		elif mText[1].lower() == "start":
			# Check if user already has instance of game running
			if gamer in games:
				games[gamer]["footer"] = "You already have a game running!"
				content = printGame(gamer)
				games[gamer]["Msg"] = await message.channel.send(embed=content)
				games[gamer]["footer"] = ""

				return

			# Initialize game
			iGame = await message.channel.send("{} started a game at {}".format(gamer[0].mention, "TIME"))
			initGame(gamer)

			games[gamer]["footer"] = 'You started a game of Eldrow!'
			content = printGame(gamer)
			games[gamer]["Msg"] = await message.channel.send(embed=content)
			games[gamer]["footer"] = ""
			
			# TODO Delete "-eldr start"
			delM(gamer, message)
			for allMsg in games[gamer]["toDel"]:
				await allMsg.delete()
			games[gamer]["toDel"] = []

			return

		# Guess word
		elif mText[1].lower() == "g":
			# Initialize game if no game yet
			if gamer not in games:
				iGame = await message.channel.send("{} started a game at {}".format(gamer[0].mention, "TIME"))
				initGame(gamer)

			# Make sure there is a guess
			if len(mText) < 3:
				games[gamer]["footer"] = '-eldr g <WORD>'
				content = printGame(gamer)
				games[gamer]["Msg"] = await message.channel.send(embed=content)
				games[gamer]["footer"] = ""
			
				# TODO Delete "-eldr g BLANK"
				delM(gamer, message)

				# Delete messages
				for allMsg in games[gamer]["toDel"]:
					await allMsg.delete()
				games[gamer]["toDel"] = []

				return

			# Make sure word is valid
			if not checkvalid(mText[2]):
				# TODO Delete "-eldr g BAD_GUESS"
				delM(gamer, message)
				delM(gamer, games[gamer]["Msg"])

				games[gamer]["footer"] = 'Guess "{}" is invalid'.format(mText[2])
				content = printGame(gamer)
				games[gamer]["Msg"] = await message.channel.send(embed=content)
				games[gamer]["footer"] = ""


				# Delete messages
				for allMsg in games[gamer]["toDel"]:
					await allMsg.delete()
				games[gamer]["toDel"] = []

				return

		

			tGuess = mText[2]
			# Go through the game
			eLogic(gamer, tGuess)
			
			# TODO Delete "-eldr g WORD" and Old Game Msg
			delM(gamer, message)
			delM(gamer, games[gamer]["Msg"])

			# Delete messages
			for allMsg in games[gamer]["toDel"]:
				await allMsg.delete()
			games[gamer]["toDel"] = []

			# edMsg = await games[gamer]["Msg"].edit(content=printGame(gamer))

			games[gamer]["turn"] += 1

			# If game is at last turn OR if game is at win, End (remove from dict)
			finito = True
			gameOver = ""
			if games[gamer]["State"]:
				games[gamer]["footer"] = 'WOOOOOT!'
				gameOver = 'Congratulations {}. You got the word! ({}/6)'.format(gamer[0].mention,str(games[gamer]["turn"]-1))
			elif games[gamer]["turn"] == 7:
				games[gamer]["footer"] = '*sad emoji noises*'
				gameOver = 'Sorry {}. The word was {}. ({}/6)'.format(gamer[0].mention, games[gamer]["answer"],str(games[gamer]["turn"]-1))
			else:
				finito = False
			
			content = printGame(gamer)
			games[gamer]["Msg"] = await message.channel.send(embed=content)
			games[gamer]["footer"] = ""
				
			if finito:
				await message.channel.send(gameOver)
				del games[gamer]

			return

		# Oops command
		elif mText[1].lower() == "oops":
			if gamer in games:
			
				# TODO Delete "-eldr oops" and Old Game Msg
				delM(gamer, message)
				delM(gamer, games[gamer]["Msg"])

				games[gamer]["footer"] = 'Here ya go!'
				content = printGame(gamer)
				games[gamer]["Msg"] = await message.channel.send(embed=content)
				games[gamer]["footer"] = ""
				
				# TODO
				# Delete messages
				for allMsg in games[gamer]["toDel"]:
					await allMsg.delete()
				games[gamer]["toDel"] = []
			
			else:
				await message.channel.send('Use command "-eldr start" to begin a game!')

			return

		# Send args
		else:
			if gamer in games:
				games[gamer]["footer"] = '"{}" is not a command. Review below!'.format(message.content.split()[1])
				content = printGame(gamer)
				games[gamer]["Msg"] = await message.channel.send(embed=content)
				games[gamer]["footer"] = ""
				
				# TODO Delete "-eldr" for no gamers
				delM(gamer, message)
				for allMsg in games[gamer]["toDel"]:
					await allMsg.delete()
					games[gamer]["toDel"] = []

			emsg = await message.channel.send(embed=eAmbed)
			if gwhere in rules:
				await rules[gwhere].delete()
			rules[gwhere] = emsg

			return
			
client.run(token)

## END Disc Client ##
