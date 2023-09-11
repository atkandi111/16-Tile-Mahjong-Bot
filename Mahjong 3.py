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
            #case_pool = [*combinations(pong + chow, length)]
            for case in combinations(pong + chow, length):
                #case = [x for meld in case for x in meld]
                case = chain(*case)
                if (Counter(case) - Counter(temp)):
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
    hand, tiles = tiles[:16], tiles[16:]
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

        #print("Suggested:", Suggest_Discard(hand, opened, discard))

        #toss = hand.index(input("Throw: "))
        #discard.append(hand.pop(toss))
        #add try-except for incorrect input

        toss = Suggest_Discard(hand, opened, discard)
        discard.append(toss)
        hand.remove(toss)
    else:
        print("Draw!")
        global draw
        draw = draw + 1
    total_discard.append(len(discard))

reference = [
        "b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8", "b9",
        "s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9",
        "c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8", "c9",
        "dN", "dE", "dW", "dS", "tG", "tR", "tW", "fR", "fB"
    ] * 4

start = time()
draw = 0
total_discard = []
for _ in range(25):
    Solo_Game()
    print("\033c", end = "")
    print(total_discard)
print("{} secs", time() - start)
print("Draws", draw)

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


#when everything is goods
#do two-sample t-test
    #check mean of discards when bot is deciding
    #check mean of discards when I am deciding
#if significantly different,
#or if mean_bot << mean_me, then
#bot-decision-making is flawed/inefficient