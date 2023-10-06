#Taiwanese Mahjong
#16-Tile Variant

from collections import Counter
from itertools import combinations, chain
from random import shuffle, choice
from time import time, sleep

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
        return (self.suit, self.unit) < (other.suit, other.unit)
    
    def __eq__(self, other):
        return (self.suit, self.unit) == (other.suit, other.unit)

    def __hash__(self):
        return hash((self.suit, self.unit))
    
    def __str__(self):
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
        self.mano = 0

    def initialize_game(self):
        self.game_status = "Ongoing"
        self.tile_wall = self.reference.copy()
        shuffle(self.tile_wall)

        self.discard = []
        self.currentplayer = self.mano
        for _ in range(4):
            self.hand.clear()
            self.open.clear()
            for _ in range(16):
                self.draw_tile()

            self.currentplayer = (self.currentplayer + 1) % 4

    @property
    def hand(self):
        return self.players[self.currentplayer].hand
    
    @property
    def open(self):
        return self.players[self.currentplayer].open
    
    @hand.setter
    def hand(self, value):
        self.players[self.currentplayer].hand = value

    @open.setter
    def open(self, value):
        self.players[self.currentplayer].open = value
    
    def draw_tile(self):
        card = self.tile_wall.pop(0)

        while len(self.tile_wall) > 14:
            if card.suit == "f":
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

    def chow_tile(self):
        card = self.discard.pop()
        self.open.append(card)
        self.hand.append(card)
        #add func for opening card

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
        if str(card) in ["fR", "fB"]:
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
        if str(card) in ["fR", "fB"]:
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

    def display(self):
        self._currentplayer = self.currentplayer
        print("\033c", end = "")
        print("Discard:", *self.discard, sep = " ")
        print("- - - - - - - - - - - - - -")
        for i in range(4):
            self.currentplayer = i
            label = ""
            if self._currentplayer == self.currentplayer: 
                label = "- current"
            print("Player {}".format(i + 1), label)
            
            print("Open:", *self.open, sep = " ")

            label = ""
            if self._currentplayer >= self.currentplayer:
                label = self.hand[-1]
            print("Grab:", label)
            
            print(*TileSet.sorter(self.hand), sep = " ")
            print("- - - - - - - - - - - - - -")
        self.currentplayer = self._currentplayer

        """print("\033c", end = "")
        print("Discard:", *self.discard, sep = " ")
        print("- - - - - - - - - - - - - -")
        for i in range(4):
            label = ""
            if self.currentplayer == i: 
                label = "- current"
            print("Player {}".format(i + 1), label)
            
            print("Open:", *self.players[i].open, sep = " ")

            label = ""
            if self.currentplayer >= i:
                label = self.players[i].hand[-1]
            print("Grab:", label)
            
            print(*TileSet.sorter(self.players[i].hand), sep = " ")
            print("- - - - - - - - - - - - - -")
        """

class Engine:
    maxcount = 0
    #tilesneeded should not be from w2
    #instead it should include all possible tilesneeded even from fullmelds
    #meldcount

    @classmethod
    def compute_discard(cls):
        """DOCSTRING
        freq represents Player's knowledge base.
        Player doesn't know tiles in tile_wall and opponents' hands.
        Player can only reference based on number of exposed tiles.
        
        Decision-making is a four-level process:
        1. Select discards that maximize number of remaining melds
        2. Select discards that maximize remaining tiles-waiting
        3. Select discards with least number of available nearby cards
        4. Randomly select from remaining candidates (equally good discard)
        """
        exposed = this.hand + this.discard
        for i in range(4):
            exposed = exposed + this.players[i].open
        freq = Counter(this.reference) - Counter(exposed)
        #new Game Class Property, freq

        candidates = this.hand.copy()
        candidates = cls.decompose_meld(candidates)
        candidates = cls.tiles_needed(candidates, freq)
        candidates = cls.near_cards(candidates, freq)
        return choice(candidates)
    
    @classmethod
    def compute_chow(cls):
        pass

    @classmethod
    def near_cards(cls, hand, freq):
        """DOCSTRING
        Isolated cards can still be ranked by usefulness
        acc. to how many tiles near it can be drawn.

        This func calculates how many near tiles
        are available for the remaining tiles.

        Ex: Hand: {1, 5, 8}
        Near 1: {1(x3), 2(x4), 3(x4)}
        Near 5: {3(x4), 4(x4), 5(x3), 6(x4), 7(x4),}
        Near 8: {6(x4), 7(x4), 8(x3), 9(x4)}

        Discarding 1 as it has the least near tiles.
        1 has the least chance of becoming a meld.
        """
        nearcount = {}
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

            nearcount[card] = sum(freq[x] for x in seqn)
        
        min_count = min(nearcount.values())
        return [x for x in hand if nearcount[x] == min_count]

    @classmethod
    def tiles_needed(cls, hand, freq):
        """DOCSTRING
        A hand can be divided into pre-melds
        with corresponding number of needed tiles.

        This func takes the remaining cards in hand
        and finds max number of needed tiles
        for each scenario that a card is discarded.

        Ex. Hand: {1, 3, 4}
        Discard 1: {2(x4), 5(x4)}
        Discard 3: {}
        Discard 4: {2(x4)}

        Discarding 1 maximizes number of tiles the
        hand could still be waiting for.

        This func takes into account the availability
        of each tiles-needed with respect to player's KB.

        Ex. 3(x1) is in the discard pile.
        Therefore, tiles-needed will only show 3(x3).
        """
        
        needtiles = {}
        needcount = {}
        for testcard in set(hand):
            needtiles[testcard] = []

            testhand = hand.copy()
            testhand.remove(testcard)
            testfreq = Counter(testhand)

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
                        if i not in needtiles[testcard]:
                            needtiles[testcard] += [i] * freq[i]

            needcount[testcard] = len(needtiles[testcard])
        
        max_count = max(needcount.values())
        return [x for x in hand if needcount[x] == max_count]

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
        meldcount = {}
        for testcard in set(hand):
            testhand = hand.copy()
            testhand.remove(testcard)
            testfreq = Counter(testhand)

            numcount = len(hand) // 3
            while not numcount < 0:
                for case in combinations(pong + chow, numcount):
                    case = chain(*case)
                    if (Counter(case) - testfreq):
                        continue

                    meldcount[testcard] = numcount
                    numcount = 0
                    break
                numcount = numcount - 1

        cls.maxcount = max(meldcount.values())
        return [x for x in hand if meldcount[x] == cls.maxcount]

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

def main():
    player_tag = this.currentplayer + 1
    #player_tag is the glow in p1 p2 p3 p4

    if len(this.hand) % 3 == 1:
        testmax, handmax = 0, 0
        if this.discard:
            testhand = this.hand + [this.discard[-1]]
            Engine.decompose_meld(testhand)
            testmax = Engine.maxcount

            Engine.decompose_meld(this.hand)
            handmax = Engine.maxcount

        if testmax > handmax:
            this.chow_tile()
            input()
        else:
            this.draw_tile()
        this.display()

        if Check_Win()[0]:
            this.game_status = "P{} Won!".format(player_tag)
            if this.mano != this.currentplayer:
                this.mano = (this.mano + 1) % 4
            return

    action = False
    if player_tag == 10:
        toss = input("Throw P{}: ".format(player_tag))
        suit, unit = toss[0], toss[1]
        if unit.isdigit(): 
            unit = int(unit)

        toss = Tile(suit, unit)
    else:
        toss = Engine.compute_discard()
        print("Throw P{}: {}".format(player_tag, toss))

        """for i in range(3, 0, -1):
            print("{}..".format(i), end = "")
            sleep(1)"""
        
        """press = input("Action: ")
        if press == "chow":
            action = True
        if press == "pass":
            action = False"""

    this.hand.remove(toss)
    #this.discard(toss)

    this._currentplayer = this.currentplayer
    for i in range(1, 4):
        this.currentplayer = (this._currentplayer + i) % 4
        if this.currentplayer == 0:
            if not action:
                continue

        this.hand.append(toss)
        if Check_Win()[0]:
            this.game_status = "P{} Won!".format(player_tag)
            if this.mano != this.currentplayer:
                this.mano = (this.mano + 1) % 4
            return
        this.hand.remove(toss)

    for i in range(1, 4):
        this.currentplayer = (this._currentplayer + i) % 4
        if this.currentplayer == 0:
            if not action:
                continue

        this.hand.append(toss)
        """if Check_Pong():
            return"""
        this.hand.remove(toss)
    this.currentplayer = this._currentplayer

    this.discard.append(toss)
    this.currentplayer = (this.currentplayer + 1) % 4

if __name__ == "__main__":
    this = Game()
    while True:
        this.initialize_game()
        while this.game_status == "Ongoing":
            main()
        print(this.game_status)
        input("Continue? ")

