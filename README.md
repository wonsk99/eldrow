# Eldrow
Discord bot for Wordle


# How it works
1. User inputs command ~eldrow start
	a. Check if User already has an instance running (return time and end)
2. Displays 3 messages as one
	a. Turn number
	b. The rows
	c. The keyboard
3. User inputs command ~eldrow guess "five letter word"
  a. Check if User inputs a valid word
    i. If invalid, replace "Turn number" with "Turn #: "WORD" is invalid!
    ii. If valid, replace "Turn number" with Turn #
	a. Also, replace the corresponding row with word and its colors
	b. Also, replace the keyboard with the corresponding colors
3. User continues to guess until end game
	a. Either user uses all 6 guesses
	b. Or user matches the word on one of 6 guesses
4. In either above case, Game will end
	a. Turn number changes to Eldrow: Win "#"/6
	b. OR Eldrow: Lose "WORD"
