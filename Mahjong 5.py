#Taiwanese Mahjong
#16-Tile Variant

from collections import Counter
from itertools import combinations, chain
from random import shuffle, choice
from time import time

print("\033c", end = "")

def Group_Sets(hand):
    freq = Counter(hand)
    pair, pong, chow = [], [], []
    pair = [[x] * 2 for x in freq if freq[x] > 1]
    pong = [[x] * 3 for x in freq if freq[x] > 2]
    chow = []
    for item in freq:
        suit, unit = item[0], item[1]
        if unit.isalpha():
            continue

        seqn = [0, 1, 2]
        seqn = [x + int(unit) for x in seqn]
        seqn = [suit + str(x) for x in seqn]

        chow += [seqn] * min([freq[x] for x in seqn])
    return pair, pong, chow

def Near_Cards(hand, freq):
    near_count = {}
    for card in set(hand):
        suit, unit = list(card)
        if unit.isalpha():
            seqn = [card]
        else:
            seqn = [-2, -1, 0, 1, 2]
            seqn = [x + int(unit) for x in seqn]
            seqn = [suit + str(x) for x in seqn]

        near_count[card] = sum([freq[x] for x in seqn])
    
    min_count = min(near_count.values())
    return [x for x in hand if near_count[x] == min_count]

def Tiles_Needed(hand, freq):
    need_count = {}
    for test_card in set(hand):
        temp = hand.copy()
        temp.remove(test_card)

        tile_needed = []
        for card in temp:
            suit, unit = list(card)
            if unit.isalpha():
                seqn = [card]

                completing_seqn = {
                    (seqn[0], seqn[0]) : (seqn[0], )
                }
            else:
                seqn = [-2, -1, 0, 1, 2]
                seqn = [x + int(unit) for x in seqn]
                seqn = [suit + str(x) for x in seqn]

                completing_seqn = {
                    (seqn[0], seqn[2]) : (seqn[1], ),
                    (seqn[1], seqn[2]) : (seqn[0], seqn[3]),
                    (seqn[2], seqn[2]) : (seqn[2], ),
                    (seqn[2], seqn[3]) : (seqn[1], seqn[4]),
                    (seqn[2], seqn[4]) : (seqn[3], )
                }

            for pre_meld, card in completing_seqn.items():
                if (Counter(pre_meld) - Counter(temp)):
                    continue
                #if pre_meld in pair, pong, or find_waiting
                for i in card:
                    if i not in tile_needed:
                        tile_needed += [i] * freq[i]

        need_count[test_card] = len(tile_needed)
    
    max_count = max(need_count.values())
    return [x for x in hand if need_count[x] == max_count]

#introduce weights for pong vs chow

def Decompose_Meld(hand, freq):
    #include eyes
    #then try to merge with check_win
    pair, pong, chow = Group_Sets(hand)
    meld_count = {}
    for test_card in set(hand):
        temp = hand.copy()
        temp.remove(test_card)

        length = len(hand) // 3
        while length >= 0:
            for case in combinations(pong + chow, length):
                if (Counter(chain(*case)) - Counter(temp)):
                    continue
                meld_count[test_card] = length
                length = 0
                break
            length = length - 1

    max_count = max(meld_count.values())
    return [x for x in hand if meld_count[x] == max_count]

def Suggest_Discard(hand, opened, discard):
    print("/////")
    discard_candidates = hand.copy()
    freq = Counter(reference) - Counter(hand + opened + discard)
    # set freq = 4 - Counter(kb) 
    # so that counter(reference) wouldnt be called anymore

    weights = [Decompose_Meld, Tiles_Needed, Near_Cards]

    for func in weights:
        discard_candidates = func(discard_candidates, freq)
        print(Sorter(discard_candidates))
    print("/////")
    return choice(discard_candidates)

    #1. Decompose hand maximizing true-melds
    #2. Decompose hand into pre-melds maximizing tiles_needed
    #3. Find remaining tiles with least number of near_cards

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
        for eye in eye_pool:
            if Counter(chain(*item, eye)) != Counter(hand):
                continue
            
            winning_case = True
            if all(x in pair for x in item):
                class_of_win = "7 Pairs"
            if all(x in pong for x in item): 
                class_of_win = "Todo Pong"
        
    return winning_case, class_of_win

def Sorter(hand):
    suit = [x for x in hand if x[1].isdigit()]
    null = [x for x in hand if x[1].isalpha()]

    return sorted(suit) + sorted(null)

def Solo_Game():
    tiles = reference.copy()

    """
    naming-scheme: class + value
    ----- classes: ball, stick, char, 
    -------------: direction, trash, flower
    """

    shuffle(tiles)
    #tiles = ['c1', 'b9', 'c8', 'b2', 'b5', 'tR', 'dN', 's8', 'dN', 'c2', 'dE', 's8', 'fR', 's3', 's1', 'b1', 'c8', 's7', 'dS', 'b8', 'b8', 'c8', 'dW', 'c7', 'c7', 'b7', 'b8', 's9', 'dW', 's2', 'c6', 'c6', 'tG', 's3', 'tR', 's2', 'dS', 's7', 'b6', 's8', 'c9', 'c4', 'b5', 'c7', 's4', 'b2', 'b2', 'b9', 'dW', 's1', 'dN', 'dW', 'b1', 'tG', 's2', 's5', 'c3', 'b6', 'c4', 'c1', 'dN', 's3', 's4', 's1', 'tW', 'c3', 'c8', 's5', 'c5', 'dS', 'b6', 'b5', 's6', 's1', 's7', 'b4', 'b3', 'c5', 'dE', 'b9', 's4', 's3', 'b4', 'b3', 's2', 'b7', 'b1', 'c9', 'dS', 'tG', 'tG', 's7', 'b3', 's6', 's9', 'b7', 'tR', 'tW', 'b5', 'c3', 'fB', 'fR', 'c1', 'c6', 'tW', 's4', 'b1', 'fR', 's8', 'c2', 'b6', 'c3', 'b4', 'dE', 'b7', 'c9', 'b8', 'c9', 'fB', 'c1', 's6', 'c5', 'fB', 'c7', 'b9', 'tR', 's5', 'c4', 's5', 'c2', 'c5', 'b3', 'tW', 'c6', 'b2', 's6', 's9', 's9', 'fB', 'c4', 'c2', 'b4', 'fR', 'dE']
    hand, tiles = tiles[:16], tiles[16:]
    hand = ['c6', 'dE', 'c2', 'b5', 'c2', 'b3', 's1', 's7', 'dW', 'b2', 'b4', 'dE', 's8', 'dW', 'b5', 'b7']
    tiles = ['s7', 'fB', 'b8', 's5', 's4', 'c1', 'c3', 'b9', 'c9', 'c2', 'fR', 'c8', 'c3', 'c1', 'c7', 'b4', 's2', 's1', 's3', 's3', 's4', 'b8', 'b4', 'c7', 'tG', 's8', 'dN', 'c6', 'c2', 's4', 'b8', 'dS', 's5', 'b9', 's9', 'b4', 'b6', 'dS', 'c4', 'b1', 'dS', 'dE', 'b5', 'b7', 'c8', 'tR', 'b3', 'b9', 'c1', 'b8', 'tR', 's2', 's6', 'c5', 's3', 's5', 's6', 'fR', 'dN', 'c8', 'tW', 'tW', 'c4', 'b1', 'c3', 's9', 'fB', 'tR', 's1', 's6', 's1', 'b2', 'c9', 's6', 'c8', 'b3', 'c3', 's9', 's4', 'b7', 'dE', 'b6', 'b6', 'c6', 's8', 'dS', 'b9', 'b7', 'tW', 'fR', 'dN', 'tW', 'c4', 'c5', 'fB', 'tG', 'c6', 'c7', 'c9', 'c4', 's3', 'b2', 's7', 'b1', 'fB', 'b2', 'c7', 'b1', 'c5', 'tR', 's2', 'tG', 'c1', 's7', 'dW', 'b5', 's8', 's5', 's2', 'c5', 'b3', 'fR', 'dN', 'c9', 's9', 'dW', 'tG', 'b6']
    opened, discard = [], []

    while len(tiles) > 13:
        print("\033c", end = "")
        print("Open:", *opened, sep = " ")
        print("Discard:", *discard, sep = " ")

        print("- - - - - - - - - - - - - -")

        print("Grab:", tiles[0])
        hand.append(tiles.pop(0))

        for idx, card in enumerate(hand):
            while card in ["fR", "fB"] and tiles:
                opened.append(card)
                card = tiles.pop()
            else:
                hand[idx] = card

        hand = Sorter(hand)
        print(*hand, sep = " ")
        if Check_Win(hand)[0]:
            print("You Won!")
            break

        print("Suggested:", Suggest_Discard(hand, opened, discard))

        #toss = hand.index(input("Throw: "))
        #discard.append(hand.pop(toss))
        #add try-except for incorrect input

        toss = Suggest_Discard(hand, opened, discard)
        discard.append(toss)
        hand.remove(toss)
    else:
        print("Draw!")
        #print(t_tiles)
    total_discard.append(len(discard))

reference = [
        "b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8", "b9",
        "s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9",
        "c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8", "c9",
        "dN", "dE", "dW", "dS", "tG", "tR", "tW", "fR", "fB"
    ] * 4

start = time()
total_discard = []
for _ in range(1):
    Solo_Game()
    print("\033c", end = "")
    print(total_discard)

print("{} secs", time() - start)

"""
Flowchart:
1. Prepare Hand and Tiles
2. Pick a tile
3. Check and replace flowers
4. Check if winning hand
5. If winning hand
    True:   stop game
            compute payment
    False:  discard a tile
            check for concealed kang
            repeat from 2
"""


#problems:
#doesn't weight pong vs chow
#doesn't know if hand is already waiting
#   if waiting, P(pong) = P(chow)
#w1 returns too many
#   if 7 8 8 9, returns 8 8
#   instead, it should be 8 only


#when everything is goods
#do two-sample t-test
    #check mean of discards when bot is deciding
    #check mean of discards when I am deciding
#if significantly different,
#or if mean_bot << mean_me, then
#bot-decision-making is flawed/inefficient