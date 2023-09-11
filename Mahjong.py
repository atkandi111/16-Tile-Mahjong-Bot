from collections import Counter
from itertools import combinations
from random import shuffle
from time import time
#Class My_Hand

start = time()

print("\033c", end = "")

tiles = [
    "b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8", "b9",
    "s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9",
    "c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8", "c9",
    "dN", "dE", "dW", "dS", "tG", "tR", "tW", "fR", "fB"
] * 4

reference = set(tiles)

def Group_Sets(hand):
    freq = Counter(hand)
    pair, pong, chow = [], [], []
    pair = [[x] * 2 for x in freq if freq[x] > 1]
    pong = [[x] * 3 for x in freq if freq[x] > 2]
    for item in freq:
        suit, unit = list(item)
        if unit.isalpha():
            continue

        seqn = [0, 1, 2]
        seqn = [x + int(unit) for x in seqn]
        seqn = [suit + str(x) for x in seqn]

        chow += [seqn] * min([freq[x] for x in seqn])
    return pair, pong, chow

def Potential_Chow(hand):
    freq = Counter(hand)
    potl, need = [], []
    for item in freq:
        suit, unit = list(item)
        if unit.isalpha():
            continue

        seqn = [-1, 0, 1, 2]
        seqn = [x + int(unit) for x in seqn]
        seqn = [suit + str(x) for x in seqn]

        lack = {
            (seqn[1], seqn[2]) : (seqn[0], seqn[3]),
            (seqn[1], seqn[3]) : (seqn[2], )
        }

        for key, val in lack.items():
            potl += [key] * min([freq[x] for x in key])
            need += [val] * min([freq[x] for x in key])
    return potl, need

def Near_Cards(hand, junk, card):
    freq = Counter(tiles) - Counter(junk)
    suit, unit = list(card)
    
    if unit.isalpha():
        seqn = [card]
    else:
        seqn = [-2, -1, 0, 1, 2]
        seqn = [x + int(unit) for x in seqn]
        seqn = [suit + str(x) for x in seqn]

    return sum([freq[x] for x in seqn]) / 20

def Compose(hand):
    pair, pong, chow = Group_Sets(hand)
    potl, need = Potential_Chow(hand)

    max_plex = 0
    plex = []

    length = len(hand) // 3
    while length:
        pool = combinations(pong + chow, length)
        for item in pool: #if list(pool)[0]:
            case = [x for nest in item for x in nest]
            if any(case.count(x) > hand.count(x) for x in case):
                continue
            xtra = hand[:]
            for item in case:
                xtra.remove(item)
            length = 0
            length_2 = len(xtra) // 2
            while length_2:
                pool_2 = combinations(pair + potl, length_2)
                for item_2 in pool_2:
                    case_2 = [x for nest in item_2 for x in nest]
                    if any(case_2.count(x) > xtra.count(x) for x in case_2):
                        continue
                    length_2 = 1
                    xtra_2 = xtra[:]
                    for item in case_2:
                        xtra_2.remove(item)
                    print(", ".join(case)) 
                    print(", ".join(case_2)) 
                    print(", ".join(xtra_2))
                    if len(case_2) > max_plex:
                        max_plex = len(case_2)
                        plex.clear()
                        plex.append(case_2)
                    if len(case_2) == max_plex:
                        plex.append(case_2)
                length_2 = length_2 - 1
        if length != 0:
            length = length - 1
    print(plex)
    return plex

    # Reminder: necessary bcoz of 6s 7s 7s 8s

    #myFunc(len(hand) // 3, "sets")
    def myFunc(length, ftype):
        while length:
            pool = combinations(pong + chow, length)
            if list(pool)[0]:
                break
            length = length - 1
        else: return

        for item in pool:
            case = [x for nest in item for x in nest]
            if any(case.count(x) > hand.count(x) for x in case):
                continue
            xtra = hand[:]
            for item in case:
                xtra.remove(item)

            match ftype:
                case "sets": return [case] + myFunc(len(hand) // 2, potl)
                case "potl": return [case, xtra]

    #return all combinations of sets and potls and xtras
    #maximize sets first, then maximize potls

    """for i in reversed(range(len(hand) // 3)):
        pool = combinations(pong + chow, i + 1)
        if pool:
            break
    """

def Check_Win(hand):
    pair, pong, chow = Group_Sets(hand)

    if len(pair) < 7:
        pool = combinations(pong + chow, len(hand) // 3)
        lock = pair
    else: #7 Pairs
        pool = combinations(pair, 7)
        lock = pong + chow

    for eye in lock:
        for item in pool:
            case = [x for nest in item for x in nest]
            if Counter(case + eye) == Counter(hand):
                if all(x in pong for x in item): 
                    print("Todo Pong")
                return True
    return False

def Find_Waiting(hand, bool):
    for card in reference:
        if Check_Win(hand + [card]):
            print(card, end = " ")
            bool = True
    return bool

def Sorter(hand):
    suit = [x for x in hand if x[1].isnumeric()]
    suit = sorted(suit, key = lambda x: list(x))

    null = [x for x in hand if x[1].isalpha()]
    null = sorted(null, key = lambda x: list(x))

    return suit + null

def Suggest_Pick(hand, junk):
    pair, pong, chow = Group_Sets(hand)
    potl, need = Potential_Chow(hand)

    case = [x for nest in pair + potl for x in nest]
    pick = [x for x in hand if x not in case]
    
    weight = {}

    freq = Counter(tiles) - Counter(hand + junk)
    for card in hand:
        weight[card] = Near_Cards(hand, junk, card)

    for match in pair:
        weight[match[0]] += Counter(hand)[match[0]] * 2.5
        # introduce bias for pairs because
        # pong is 2x more likely than chow
        # change 2.5
        # instead weigh number of potl, sets, pong
        # seq1 takes priority to seq2

    for idx, match in enumerate(potl):
        weight[match[0]] += sum([freq[x] for x in need[idx]])
        weight[match[1]] += sum([freq[x] for x in need[idx]])
    
    for match in potl:
        weight[match[0]] -= case.count(match[1]) // len(case)
        weight[match[1]] -= case.count(match[0]) // len(case)

    """
    for elem in weight.items():
        print(elem)
    """

    keys = list(weight.keys())
    shuffle(keys)
    return min(keys, key = weight.get)

    #If None,
    #Randomly Choose To Break
    #1) If many meld, break meld
    #2) If many pair, break pair
    # counter number of pairs, number of potl
    # divide num by total num
    # subtract division to weight
    #Unless pair_num >= 5

    #Instead
    #Compose all possible pairs and sets and potls
    #Show all compositions with least set count
    #Show all sets with least need and near_card

def Solo_Game(tiles):
    shuffle(tiles)
    hand, tiles, junk = tiles[:16], tiles[16:], []
    xhand = ['b3', 'b5', 'b6', 'b8', 
            'c2', 'c4', 'c7', 'c8', 
            'c8', 's2', 's3', 's4', 
            'dE', 'dE', 'dS', 'dS']
    xhand = ['b1', 'b3', 'b4', 'b9',
            'b9', 's7', 's8', 'b6',
            's9', 'c1', 'c3', 'c4',
            'c6', 'c7', 'c8', 'c9']
    while tiles:
        print("\033c", end = "")
        print("Discard:", " ".join(junk), "\n")

        """
        print("Grab:", "s8")
        hand.append("s8")
        """
        print("Grab:", tiles[0])
        hand.append(tiles.pop(0))

        flower = []
        for card in hand:
            if card[0] == "f" and tiles:
                flower.append(tiles[-1])
                hand.remove(card)
                hand.append(tiles.pop())
        if flower:
            print("Flower:", *flower, sep = " ")

        print(" ".join(Sorter(hand)))
        if Check_Win(hand):
            print("You Won!")
            break
        print("Suggested:", Suggest_Pick(hand, junk))
        Compose(hand)

        toss = hand.index(input("Throw: "))
        #junk.append(hand.pop(hand.index(Suggest_Pick(hand, junk))))
        junk.append(hand.pop(toss))

Solo_Game(tiles)

end = time()
print("--- %s seconds ---" % (end - start))