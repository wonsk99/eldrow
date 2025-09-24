# Stole the list of words from Wordle
with open('../data/fulldict.txt') as f:
	words = f.readline()

# Parse it to make it more readable
with open('../data/complete.txt', "w") as f:
	for word in words.split(","):
		f.write(word.strip()[1:-1] + "\n")
