import discord
import json
import random
import string

# EMOJI DICt
with open("data/emoji_dict.json") as f:
    EMOJI_DICT = json.load(f)
f.close()

# LET'S GET OUR VALID WORDS
DICT_PATH = "data/complete.txt"
# For ease of searching
SEARCH_DICT = set()
# For sake of randomizing
LIST_DICT = []

with open(DICT_PATH) as f:
	for word in f.readlines():
		LIST_DICT.append(word.upper().strip())
		SEARCH_DICT.add(word.upper().strip())

# DISPLAY KEYBOARD
KEYS = []
KEYS.append(list("QWERTYUIOP"))
KEYS.append(list(" ASDFGHJKL"))
KEYS.append(list("  ZXCVBNM"))
SPACE = "ㅤ"

class Board:
    def __init__(self, gamer):
        self.gamer = gamer
        self.answer = self.new_game_word()

        self.greens = set()
        self.yellows = set()
        self.blacks = set()

        self.mode = "gray"

        self.msg = ""
        self.footer = ""
        self.turn = 1

        self.guesses = [[EMOJI_DICT[f"BLANK_{self.mode}"]] * 5] * 6

    ### START
    def new_game_word(self):
        ans = LIST_DICT[random.randint(0,len(LIST_DICT))].strip().upper()
        return ans

    async def start_game(self, interaction):
        await self.delete_msg(self.msg)

        await self.print_game(interaction)

    ### GUESS
    async def guess_word(self, interaction, word):
        finito = False
        await self.delete_msg(self.msg)

        # Check if valid
        if word not in SEARCH_DICT:
            self.footer = f"{word} is Invalid"
        # Check letters
        else:
            winner = self.check_letters(word)

            self.turn += 1
            finito = False
            if winner:
                self.footer = f"Congratulations! {self.turn-1}/6"
                finito = True
            elif self.turn > 6:
                self.footer = f"Beep Beep. You lost! The word was {self.answer}"
                finito = True

        await self.print_game(interaction)

        return finito

    def check_letters(self, guess):
        line = []

        corrects = 0
        print(self.answer)

        counter = {}
        for letter in self.answer:
            counter[letter] = counter.get(letter, 0) + 1

        seen_counter= {}
        res = [""] * 5

        for i in range(5):
            # Check Green
            if guess[i] == self.answer[i]:
                res[i] = self.get_color(guess[i], "green")
                corrects += 1

                seen_counter[guess[i]] = seen_counter.get(guess[i], 0) + 1
                
                self.greens.add(guess[i])
        
        for i in range(5):
            if res[i]:
                continue

            seen = seen_counter.get(guess[i], 0)
            left = counter.get(guess[i], 0)

            # Check Yellow
            if guess[i] in self.answer and seen < left:
                res[i] = self.get_color(guess[i], "yellow")
                seen_counter[guess[i]] = seen + 1

                if guess[i] not in self.greens:
                    self.yellows.add(guess[i])
            # It's Black
            else:
                res[i] = self.get_color(guess[i], "black")
                if guess[i] not in self.greens and guess[i] not in self.yellows:
                    self.blacks.add(guess[i])

        self.guesses[self.turn-1] = res

        if corrects == 5:
            return True
        return False

    def get_color(self, letter, color):
        code = f"{letter}_{color}"
        print(code)

        return EMOJI_DICT[code]

    ### DISPLAY
    async def delete_msg(self, message):
        if isinstance(message, discord.message.Message):
            await message.delete()

    def display_board(self):
        full_board = ""
        for ct, guess in enumerate(self.guesses):
            row = "{}. ".format(str(ct+1))
            for letter in guess:
                row += letter
                row += " "
            row += "\n"
            full_board += row
        return full_board + "\n"
    
    def display_keys(self):
        display_row = ""
        for keyrow in KEYS:
            for key in keyrow:
                if not key.strip():
                    display_key = SPACE
                elif key in self.greens:
                    display_key = self.get_color(key, "green")
                elif key in self.yellows:
                    display_key = self.get_color(key, "yellow")
                elif key in self.blacks:
                    display_key = self.get_color(key, "black")
                else:
                    display_key = self.get_color(key, "gray")
                display_row += display_key
                display_row += " "
            display_row += "\n"
        return display_row

    async def print_game(self, interaction):
        tUser = "{}'s game".format(self.gamer.display_name)
        tBoard = self.display_board()
        tKeys = self.display_keys()
        
        # Create embed
        e = discord.Embed(title=tUser, description=tBoard+tKeys, color=0x00ff00)
        e.set_footer(text=self.footer)

        await interaction.response.defer()
        self.msg = await interaction.followup.send(content=self.gamer.mention, embed=e)

        self.footer = ""