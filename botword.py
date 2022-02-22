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

	return

# Generate a random word to guess
def genWord():
	return LISTED[random.randint(0,len(LISTED))].strip().upper()

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
	return tBoard

# Print function
def printGame(gamer):
	tBoard = dispBoard(gamer)
	tKeys = dispKeys(gamer)
	fullText = tBoard + tKeys
	return fullText

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
Available commands:
			-elword start
			-elword guess <WORD>
			-elword oops (Use this when the game disappears from your screen)
Rules:
			**Bolds** are right word in the right spot
			__Underlines__ are in the word in the wrong spot
			~~Strikethroughs~~ are not in the word
'''

## GLOBALS ##
# Running Games
games = {}

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
	gamer = message.author
	# Ignore messages from bot itself
	if gamer == client.user:
		return
	
	# Receive message that begins with eldrow
	if message.content.startswith('-eldrow'):
		# Parse message
		mText = message.content.split()
		if len(mText) < 2:
			argMsg = await message.channel.send(eArgs)
			if gamer in games:
				delM(gamer, message)
				delM(gamer, argMsg)
			return

		# Game Start
		if mText[1].lower() == "start":
			# Check if user already has instance of game running
			if gamer in games:
				alMsg = await message.channel.send('{}. You already have a game running!'.format(gamer.mention))
				delM(gamer, message)
				delM(gamer, alMsg)
				return
			await message.channel.send('{}. You started a game of Eldrow!'.format(gamer.mention))

			# Initialize game
			initGame(gamer)
			content = printGame(gamer)
			gamemsg = await message.channel.send("{}'s Game\n{}".format(gamer.mention, content))
			games[gamer]["Msg"] = gamemsg


			print(games[gamer]["answer"])
			return

		# Guess word
		elif mText[1].lower() == "guess":
			# Make sure there is a guess
			if len(mText) < 3:
				reMsg = await message.channel.send('-eldrow guess <WORD>')
				delM(gamer, message)
				delM(gamer, reMsg)
				return

			# Make sure word is valid
			if not checkvalid(mText[2]):
				reMsg = await message.channel.send('Guess is invalid')
				delM(gamer, message)
				delM(gamer, reMsg)
				return

			# Initialize game if no game yet
			if gamer not in games:
				await message.channel.send('{}. You started a game of Eldrow!'.format(gamer.mention))
				
				initGame(gamer)
				content = printGame(gamer)
				gamemsg = await message.channel.send("{}'s Game\n{}".format(gamer.mention, content))
				games[gamer]["Msg"] = gamemsg

			tGuess = mText[2]
			# Go through the game
			eLogic(gamer, tGuess)

			edMsg = await games[gamer]["Msg"].edit(content=printGame(gamer))
			delM(gamer, message)

			games[gamer]["turn"] += 1

			for allMsg in games[gamer]["toDel"]:
				await allMsg.delete()
			games[gamer]["toDel"] = []
			
			# If game is at last turn OR if game is at win, End (remove from dict)
			if games[gamer]["State"]:
				await message.channel.send('Congratulations {}. You got the word!'.format(gamer.mention))
				del games[gamer]
			if games[gamer]["turn"] == 7:
				await message.channel.send('Sorry {}. The word was {}'.format(gamer.mention, games[gamer]["answer"]))
				del games[gamer]

			print(games[gamer]["Greens"])
			
			return

		# Oops command
		elif mText[1].lower() == "oops":
			if gamer in games:
				delM(gamer, message)
				delM(gamer, games[gamer]["Msg"])
				gamemsg = await message.channel.send(games[gamer]["Msg"].content)
				games[gamer]["Msg"] = gamemsg
				for allMsg in games[gamer]["toDel"]:
					await allMsg.delete()
				games[gamer]["toDel"] = []
				return

		# Send args
		else:
			esMsg = await message.channel.send(eArgs)
			if gamer in games:
				delM(gamer, message)
				delM(gamer, esMsg)
			return


client.run(token)

## END Disc Client ##
