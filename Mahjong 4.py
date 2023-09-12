#Taiwanese Mahjong
#16-Tile Variant

from collections import Counter
from itertools import combinations
from random import shuffle, choice
from time import time

print("\033c", end = "")

class Player:
    id = 0
    def __init__(self):
        Player.id = Player.id + 1
        self.hand = []
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
        for i in range(4):
            self.current_player = i
            self.players.append(Player())
            self.hand = [self.draw_tile() for _ in range(16)]

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
    
    def draw_tile(self):
        card = self.tile_wall.pop(0)

        while len(self.tile_wall) > 13:
            if card.__repr__() in ["fR", "fB"]:
                self.open.append(card)
                card = self.tile_wall.pop()
                continue
            
            if self.hand.count(card) + 1 == 4:
                self.open.append(card)
                for _ in range(3):
                    self.open.append(card)
                    self.hand.remove(card)
                card = self.tile_wall.pop()
                continue
            
            return card
        self.game_status = "Draw"

    """
    def draw_tile2(self):
        if len(self.tile_wall) < 14:
            self.game_status = "Draw"
            return
        return self.open_flwr(self.tile_wall.pop(0))

    def open_flwr(self):
        if len(self.tile_wall) < 14:
            self.game_status = "Draw"
            return
        
        card = self.tile_wall.pop()
        if card.__repr__() in ["fR", "fB"]:
            self.open.append(card)
            card = self.open_flwr()

        if self.hand.count(card) + 1 == 4:
            self.open.append(card)
            for _ in range(3):
                self.open.append(card)
                self.hand.remove(card)
            card = self.open_flwr()

        return card
    
    
    def draw_flwr(self):
        if len(self.tile_wall) < 14:
            self.game_status = "Draw"
            return
        return self.open_flwr(self.tile_wall.pop())

    def open_flwr2(self, card):
        if card.__repr__() in ["fR", "fB"]:
            self.open.append(card)
            card = self.draw_flwr()

        if self.hand.count(card) + 1 == 4:
            self.open.append(card)
            for _ in range(3):
                self.open.append(card)
                self.hand.remove(card)
            card = self.draw_flwr()

        return card
    """

    def toss_tile(self, tile):
        pass

def Group_Sets():
    freq = Counter(this.hand)
    pair = [[x] * 2 for x in freq if freq[x] > 1]
    pong = [[x] * 3 for x in freq if freq[x] > 2]
    chow = []
    for card in freq:
        if isinstance(card.unit, str):
            continue

        seqn = [
            Tile(card.suit, card.unit),
            Tile(card.suit, card.unit + 1),
            Tile(card.suit, card.unit + 2)
        ]
        
        chow += [seqn] * min([freq[x] for x in seqn])
    return pair, pong, chow

def Check_Win():
    pair, pong, chow = Group_Sets()
    winning_case = False
    class_of_win = "Standard"

    if len(pair) < 7:
        case_pool = combinations(pong + chow, len(this.hand) // 3)
        eye_pool = pair
    else: #7 Pairs
        case_pool = combinations(pair, 7)
        eye_pool = pong + chow

    for item in case_pool:
        case = [x for meld in item for x in meld]
        for eye in eye_pool:
            if Counter(case + eye) != Counter(this.hand):
                continue
            
            winning_case = True
            if all(x in pair for x in item):
                class_of_win = "7 Pairs"
            if all(x in pong for x in item): 
                class_of_win = "Todo Pong"
    
    return winning_case, class_of_win

def Display():
    print("\033c", end = "")
    print("Discard:", *this.discard, sep = " ")
    print("- - - - - - - - - - - - - -")
    for i in range(4):
        label = ""
        if this.current_player == i: 
            label = "- current"
        print("Player {}".format(i + 1), label)
        
        print("Open:", *this.players[i].open, sep = " ")

        label = ""
        if this.current_player >= i:
            label = this.players[i].hand[-1]
        print("Grab:", label)
        
        print(*TileSet.sorter(this.players[i].hand), sep = " ")
        print("- - - - - - - - - - - - - -")


def main2():
    #print("\033c", end = "")
    print("Discard:", *this.discard, sep = " ")
    print("- - - - - - - - - - - - - -")
    for i in range(4):
        this.current_player = i
        print("Player {}".format(i + 1))

        this.hand.append(this.draw_tile())
        if this.game_status != "Ongoing":
            return
        
        print("Open:", *this.open, sep = " ")
        print("Grab:", this.hand[-1])

        print(*TileSet.sorter(this.hand), sep = " ")
        if Check_Win(this.hand)[0]:
            this.game_status = "Player {} Won!".format(i + 1)
            return

        toss = input("Throw: ")
        for idx, card in enumerate(this.hand):
            if card.__repr__() != toss:
                continue
            this.discard.append(this.hand.pop(idx))
            break
        else:
            raise ValueError("Tile not in hand")

        print("- - - - - - - - - - - - - -")
        
def main():
    #print("\033c", end = "")
    for i in range(4):
        this.current_player = i
        this.hand.append(this.draw_tile())

        Display()
        
        if Check_Win()[0]:
            this.game_status = "Player {} Won!".format(i + 1)
            return

        toss = input("Throw P{}: ".format(i + 1))
        for idx, card in enumerate(this.hand):
            if card.__repr__() == toss:
                this.discard.append(this.hand.pop(idx))
                break
        else:
            raise ValueError("Tile not in hand")

if __name__ == "__main__":
    this = Game()
    while this.game_status == "Ongoing":
        main()
    print(this.game_status)

