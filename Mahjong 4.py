#Taiwanese Mahjong
#16-Tile Variant

from collections import Counter
from itertools import combinations, chain
from random import shuffle, choice
from time import time

print("\033c", end = "")

class Player:
    def __init__(self):
        self.hand = []
        self.open = []
        self.points = 0

class Tile:
    def __init__(self, suit, unit):
        self.suit = suit
        self.unit = unit

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
        suit = [x for x in hand if isinstance(x.unit, int)]
        null = [x for x in hand if isinstance(x.unit, str)]

        return sorted(suit) + sorted(null)

class Game:
    def __init__(self):
        self.players = [Player() for _ in range(4)]
        self.reference = TileSet().reference
        self.current_player = 0
        self.mano = 0

    def initialize_game(self):
        self.game_status = "Ongoing"
        self.tile_wall = self.reference.copy()
        shuffle(self.tile_wall)

        self.discard = []
        for i in range(4):
            self.current_player = i
            self.hand.clear()
            self.open.clear()
            for _ in range(16):
                self.draw_tile()

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

        while len(self.tile_wall) > 14:
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

            self.hand.append(card)
            break
        else:
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

class Engine():
    @classmethod
    def compute_discard(cls):
        """DOCSTRING
        freq represents the Player's knowledge base.
        Player don't know tiles in tile_wall and opponents' hands.
        Player can only reference based on number of exposed tiles.
        
        Decision-making is a four-level process.
        1. Select discards that maximize number of remaining melds
        2. Select discards that maximize remaining tiles-waiting
        3. Select discards with least number of available nearby cards
        4. Randomly select from discard candidates (equally good discard)
        """
        freq = Counter(this.reference) - Counter(this.hand + this.open + this.discard)

        diskcand = this.hand.copy()
        diskcand = cls.decompose_meld(diskcand)
        diskcand = cls.tiles_needed(diskcand, freq)
        diskcand = cls.near_cards(diskcand, freq)
        return choice(diskcand)

    @classmethod
    def near_cards(cls, hand, freq):
        near_count = {}
        for card in set(hand):
            if isinstance(card.unit, str):
                seqn = [card]
            else:
                seqn = [
                    Tile(card.suit, card.unit - 2),
                    Tile(card.suit, card.unit - 1),
                    Tile(card.suit, card.unit),
                    Tile(card.suit, card.unit + 1),
                    Tile(card.suit, card.unit + 2)
                ]

            near_count[card] = sum([freq[x] for x in seqn])
        
        min_count = min(near_count.values())
        return [x for x in hand if near_count[x] == min_count]

    @classmethod
    def tiles_needed(cls, hand, freq):
        """DOCSTRING
        A hand can be divided into pre-melds
        with corresponding number of tiles-needed.

        This func takes the remaining cards in hand
        and finds max number of tiles-needed
        for each scenario that a card is discarded.

        Ex. Hand: {1, 3, 4}
        Discard 1: {2(x4), 5(x4)}
        Discard 3: {}
        Discard 4: {2(x4)}

        Discarding 1 maximizes number of tiles the
        hand could still be waiting for.

        This func takes into account the availability
        for each tiles-needed with respect to player's KB.

        Ex. 3(x1) is in the discard pile.
        Therefore, tiles-needed will only show 3(x3).
        """
        
        need_count = {}
        for testcard in set(hand):
            testhand = hand.copy()
            testhand.remove(testcard)
            testfreq = Counter(testhand)

            tile_needed = {}
            for card in set(testhand):
                if isinstance(card.unit, str):
                    completing_seqn = {
                        (card, card) : (card, )
                    }
                else:
                    seqn = [
                        Tile(card.suit, card.unit - 2),
                        Tile(card.suit, card.unit - 1),
                        Tile(card.suit, card.unit),
                        Tile(card.suit, card.unit + 1),
                        Tile(card.suit, card.unit + 2)
                    ]

                    completing_seqn = {
                        (seqn[0], seqn[2]) : (seqn[1], ),
                        (seqn[1], seqn[2]) : (seqn[0], seqn[3]),
                        (seqn[2], seqn[2]) : (seqn[2], ),
                        (seqn[2], seqn[3]) : (seqn[1], seqn[4]),
                        (seqn[2], seqn[4]) : (seqn[3], )
                    }

                for pre_meld, cmp_meld in completing_seqn.items():
                    if (Counter(pre_meld) - testfreq):
                        continue
                    for i in cmp_meld:
                        tile_needed[i] = freq[i]

            need_count[testcard] = sum(tile_needed.values())
        
        max_count = max(need_count.values())
        return [x for x in hand if need_count[x] == max_count]

    @classmethod
    def decompose_meld(cls, hand):
        """DOCSTRING
        A hand can be divided into meld-holders.

        This func finds max number of meld-holders
        for each scenario that a card is discarded.

        Ex. Hand: {1, 2, 3, 4}
        Discard 1: {2, 3, 4}
        Discard 2: {}
        Discard 3: {}
        Discard 4: {1, 2, 3}

        Discarding 1 | 4 maximizes remaining melds.
        Therefore, 1 | 4 are good discard candidates.
        """

        pair, pong, chow = Group_Sets()
        maxholder, numholder = 0, 0
        nullcards = []

        for testcard in set(hand):
            testhand = hand.copy()
            testhand.remove(testcard)
            testfreq = Counter(testhand)

            numholder = len(hand) // 3
            while not numholder < maxholder:
                for case in combinations(pong + chow, numholder):
                    case = chain(*case)
                    if (Counter(case) - testfreq):
                        continue

                    if maxholder < numholder:
                        maxholder = numholder
                        nullcards.clear()
                    nullcards.append(testcard)
                    break
                numholder = numholder - 1

        return [x for x in hand if x in nullcards]

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
        
        chow += [seqn] * min(freq[x] for x in seqn)
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

def Display(current_idx):
    print("\033c", end = "")
    print("Discard:", *this.discard, sep = " ")
    print("- - - - - - - - - - - - - -")
    for i in range(4):
        this.current_player = i
        label = ""
        if current_idx == i: 
            label = "- current"
        print("Player {}".format(i + 1), label)
        
        print("Open:", *this.open, sep = " ")

        label = ""
        if current_idx >= i:
            label = this.hand[-1]
        print("Grab:", label)
        
        print(*TileSet.sorter(this.hand), sep = " ")
        print("- - - - - - - - - - - - - -")
    this.current_player = current_idx

def main():
    this.current_player = (this.current_player + 1) % 4
    player_tag = this.current_player + 1

    this.draw_tile()
    Display(this.current_player)
    
    if Check_Win()[0]:
        this.game_status = "P{} Won!".format(player_tag)
        if this.mano != this.current_player:
            this.mano = (this.mano + 1) % 4
        return

    if player_tag == 1:
        toss = input("Throw P{}: ".format(player_tag))
    else:
        toss = Engine.compute_discard()
        print("Throw P{}: {}".format(player_tag, toss))

    idx = this.hand.index(repr(toss))
    this.discard.append(this.hand.pop(idx))
    """for idx, card in enumerate(this.hand):
        if repr(card) == repr(toss):
            this.discard.append(this.hand.pop(idx))
            break
    else:
        raise ValueError("Tile not in hand")"""

if __name__ == "__main__":
    this = Game()
    while True:
        this.initialize_game()
        while this.game_status == "Ongoing":
            main()
        print(this.game_status)
        input("Continue? ")

