# Eldrow
Discord bot for Wordle


# How it works
1. User inputs command -eldrow start
   - Check if User already has an instance running (return time and end)
2. Displays 3 messages as one
   - Turn number
   - The rows
   - The keyboard
3. User inputs command -eldrow guess "five letter word"
   - Check if User inputs a valid word
   - If invalid, replace "Turn number" with "Turn #: "WORD" is invalid!
     - If valid, replace "Turn number" with Turn #
       - a. Also, replace the corresponding row with word and its colors
       - b. Also, replace the keyboard with the corresponding colors
3. User continues to guess until end game
   - Either user uses all 6 guesses
   - Or user matches the word on one of 6 guesses
4. In either above case, Game will end
   - a. Turn number changes to Eldrow: Win "#"/6
   - b. OR Eldrow: Lose "WORD"
