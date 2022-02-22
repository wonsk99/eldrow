## Wordle clone (Fun on the command line!)
import random

DICT = "complete.txt"
FULL = set()
LISTED = []
with open(DICT) as f:
	for word in f.readlines():
		LISTED.append(word.strip())
		FULL.add(word.strip())

BOARD = [[" "]*5]*6
GAMESTATE = 0
TARGET = ""

KEYS = []
KEYS.append(list("QWERTYUIOP"))
KEYS.append(list("ASDFGHJKL"))
KEYS.append(list("ZXCVBNM"))

GREENS = set()
YELLOWS = set()
GRAYS = set()

class colors:
	G = '\033[37;1m\33[42;1m'
	Y = '\033[37;1m\33[43;1m'
	N = '\033[37;1m\33[40;1m'
	U = '\033[37;1m\33[100;1m'
	F = '\033[37;1m\33[0m'

# Display used keys
def keyboard():
	global KEYS
	global GREENS
	global YELLOWS
	global GRAYS
	for key in KEYS:
		for l in key:
			if l in GREENS:
				p = color(l, colors.G)
			elif l in YELLOWS:
				p = color(l, colors.Y)
			elif l in GRAYS:
				p = color(l, colors.N)
			else:
				p = color(l, colors.U)
			print(p, end=" ")
		print("\n")

# Generate word
def generate():
	return LISTED[random.randint(0,len(LISTED))].strip().upper()

# Display Board
def display():
	# TOP
	print("+-" * 5, end="")
	print("+")
	
	# BOARD
	for row in BOARD:
		for letter in row:
			print("|{}".format(letter), end="")
		print("|\n", end="")
		print("+-" * 5, end="")
		print("+")

	# KEYBOARD
	keyboard()

# Guess Word
def eldrow(word, rem):
	global GREENS
	global YELLOWS
	global GRAYS
	global TARGET
	global GAMESTATE

	word = list(word.upper())
	unchecked = set([0,1,2,3,4])

	# Green
	for i in range(0,5):
		if word[i] == TARGET[i]:
			rem = checkr(word[i], rem)
			GREENS.add(word[i])
			word[i] = color(word[i], colors.G)
			unchecked.remove(i)

	if len(rem) <= 0:
		BOARD[GAMESTATE] = word
		return False

	# Yellow
	for i in range(0,5):
		if word[i] in rem:
			rem = checkr(word[i], rem)
			if word[i] not in GREENS:
				YELLOWS.add(word[i])
			word[i] = color(word[i], colors.Y)
			unchecked.remove(i)

	# Gray
	for i in unchecked:
		if word[i] not in GREENS:
			GRAYS.add(word[i])
		word[i] = color(word[i], colors.N)

	BOARD[GAMESTATE] = word

	return True
	
# Checker if letter still in
def checkr(letter, rem):
	rem[letter] -= 1
	if rem[letter] == 0:
		del rem[letter]
	return rem

# Color
def color(letter, c):
	return(c + letter + colors.F)

# Set of solution letters
def setrem():
	global TARGET
	rem = {}
	for l in TARGET:
		if l not in rem:
			rem[l] = 0
		rem[l] += 1

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
	
# MAIN
#
#
if __name__ == "__main__":
	# Generate word
	TARGET = generate()

	# Get set of letters
	rems = setrem()
	GUESSED = True

	while GAMESTATE < 6 and GUESSED:
		display()
		guess = input("Guess: ")
		while not checkvalid(guess):
			print("Invalid!")
			guess = input("Guess: ")

		GUESSED = eldrow(guess, dict(rems))
		GAMESTATE += 1
	
	display()
	if GUESSED:
		print("LOSE!")
		print(TARGET)
	else:
		print("WIN!")
