#Taiwanese Mahjong
#16-Tile Variant

from collections import Counter
from itertools import combinations
from random import shuffle, choice
from time import time

print("\033c", end = "")

class Player:
    id = 0
    def __init__(self, hand):
        Player.id = Player.id + 1
        self.hand = hand
        self.open = []
        self.points = 0

class Bot:
    pass

class Tile:
    def __init__(self, suit, unit):
        self.suit = suit
        self.unit = unit

    def __getitem__(self, index):
        match index:
            case 0: return self.suit
            case 1: return self.unit

    def __lt__(self, other):
        return self.__repr__() < other.__repr__()    
    
    def __eq__(self, other):
        return self.__repr__() == other.__repr__()

    def __hash__(self):
        return hash((self.suit, self.unit))

    def __repr__(self):
        return f"{self.suit}{self.unit}"

class TileSet:
    def __init__(self):
        self.reference = []

        constructor = {
            "b" : range(1, 10),
            "s" : range(1, 10),
            "c" : range(1, 10),
            "d" : ("N", "S", "W", "E"),
            "t" : ("G", "R", "W"),
            "f" : ("R", "B")
        }

        for suit in constructor:
            for unit in constructor[suit]:
                for _ in range(4): 
                    self.reference.append(Tile(suit, unit))

    @staticmethod
    def sorter(hand):
        suit = [x for x in hand if isinstance(x[1], int)]
        null = [x for x in hand if isinstance(x[1], str)]

        return sorted(suit) + sorted(null)

class Game:
    def __init__(self):
        self.game_status = "Ongoing"
        self.tile_wall = TileSet().reference
        shuffle(self.tile_wall)
        self.discard = []

        self.players = []
        self.current_player = None
        self.mano = 0
        for _ in range(4):
            self.players.append(Player(self.draw_tile(16)))

    @property
    def hand(self):
        return self.players[self.current_player].hand
    
    @property
    def open(self):
        return self.players[self.current_player].open
    
    @hand.setter
    def hand(self, value):
        self.players[self.current_player].hand = value

    @open.setter
    def open(self, value):
        self.players[self.current_player].open = value

    def draw_tile(self, number = 1):
        if len(self.tile_wall) < 14:
            self.game_status = "Draw"
        tile_drawn = self.tile_wall[:number]
        self.tile_wall = self.tile_wall[number:]
        return tile_drawn

    def draw_flwr(self):
        if len(self.tile_wall) < 14:
            self.game_status = "Draw"
        return self.tile_wall.pop()

    def open_tile(self, tile):
        pass

    def toss_tile(self, tile):
        pass

def Group_Sets(hand):
    freq = Counter(hand)
    pair = [[x] * 2 for x in freq if freq[x] > 1]
    pong = [[x] * 3 for x in freq if freq[x] > 2]
    chow = []
    for item in freq:
        suit, unit = item[0], item[1]
        if isinstance(unit, str):
            continue

        seqn = [0, 1, 2]
        seqn = [x + int(unit) for x in seqn]
        seqn = [suit + str(x) for x in seqn]

        chow += [seqn] * min([freq[x] for x in seqn])
    return pair, pong, chow

def Check_Win(hand):
    pair, pong, chow = Group_Sets(hand)
    winning_case = False
    class_of_win = "Standard"

    if len(pair) < 7:
        case_pool = combinations(pong + chow, len(hand) // 3)
        eye_pool = pair
    else: #7 Pairs
        case_pool = combinations(pair, 7)
        eye_pool = pong + chow

    for item in case_pool:
        case = [x for meld in item for x in meld]
        for eye in eye_pool:
            if Counter(case + eye) != Counter(hand):
                continue
            
            winning_case = True
            if all(x in pair for x in item):
                class_of_win = "7 Pairs"
            if all(x in pong for x in item): 
                class_of_win = "Todo Pong"
    
    return winning_case, class_of_win

def main():
    #print("\033c", end = "")
    print("Discard:", *this.discard, sep = " ")
    print("- - - - - - - - - - - - - -")
    for i in range(4):
        this.current_player = i
        print("Player {}".format(i + 1))
        this.hand.append(open_flwr(*this.draw_tile()))

        def open_flwr(card, idx = -1):
            while card.__repr__() in ["fR", "fB"]:
                this.open.append(card)
                card = this.draw_flwr()

            if this.hand.count(card) == 4:
                for _ in range(4):
                    this.open.append(card)
                    this.hand.remove(card)
                card = open_flwr(this.draw_flwr())
            
            card

        freq = Counter(this.hand)
        kang = [x for x in freq if freq[x] > 3]
        for card in kang:
            this.hand.append(open_flwr(card))

        if this.game_status != "Ongoing":
            return
        
        print("Open:", *this.open, sep = " ")
        print("Grab:", this.hand[-1])

        print(*TileSet.sorter(this.hand), sep = " ")
        if Check_Win(this.hand)[0]:
            this.game_status = f"Player {i} Won!"
            return

        toss = input("Throw: ")
        for idx, card in enumerate(this.hand):
            if card.__repr__() != toss:
                continue
            this.discard.append(card)
            del this.hand[idx]
            break
        else:
            raise ValueError("Tile not in hand")

        print("- - - - - - - - - - - - - -")
        
if __name__ == "__main__":
    this = Game()
    while this.game_status == "Ongoing":
        main()
    print(this.game_status)

