class Gamer:
    def __init__(self, title, cards):
        self.state = 0
 
        self.title = title
        self.cards = cards

        self.elapsed = {}