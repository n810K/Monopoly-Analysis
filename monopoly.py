import argparse
import os
import random
import sys

import pandas as pd

#40 Squares in Monopoly. Rows 40 and 41 split square 10 apart, so 10 = 40 + 41.

BOARD_SIZE = 40
GO = 0
JAIL = 10
GO_TO_JAIL = 30

CHANCE_SPACES = (7, 22, 36)
CHEST_SPACES = (2, 17, 33)
RAILROADS = (5, 15, 25, 35)
UTILITIES = (12, 28)

JUST_VISITING = 40
IN_JAIL = 41

SPACE_NAMES = [
    "Go", "Medit.", "C. Chest (0)", "Baltic", "I. Tax",
    "R. Railroad", "Oriental", "Chance (0)", "Vermont", "Connecticut",
    "Jail + Visiting", "St. Charles", "El. Company", "States", "Virginia",
    "Penns Railroad", "St. James", "C. Chest (1)", "Tennessee", "New York",
    "Free Parking", "Kentucky", "Chance (1)", "Indiana", "Illinois",
    "B&O Railroad", "Atlantic", "Ventnor", "Water Works", "Marvin Gardens",
    "Go to Jail", "Pacific", "North Carolina", "C. Chest (2)", "Pennsylvania",
    "Short Line", "Chance (2)", "Park Place", "Luxury Tax", "Boardwalk",
    "Just Visiting", "In Jail",
]

"""
Chance, 16 cards, 10 of which move you:
1) Advance to Go (0)
2) Advance to Illinois Avenue (24)
3) Advance to St. Charles Place (11)
4) Advance to Boardwalk (39)
5) Take a ride on the Reading Railroad (5)
6) Advance to nearest Utility (12, 28)
7) Advance to nearest Railroad (5, 15, 25, 35) -- there are two of these
8) Go to Jail (10)
9) Go back 3 spaces
The other 6 are money cards and never move the token.
"""
CHANCE_DECK = [
    ("advance", GO),
    ("advance", 24),
    ("advance", 11),
    ("advance", 39),
    ("advance", 5),
    ("nearest", UTILITIES),
    ("nearest", RAILROADS),
    ("nearest", RAILROADS),
    ("jail", None),
    ("back", 3),
] + [(None, None)] * 6

"""
Community Chest, 16 cards. Only two of them move you:
1) Advance to Go (0)
2) Go to Jail (10)
"""
CHEST_DECK = [
    ("advance", GO),
    ("jail", None),
] + [(None, None)] * 14


class Stats:
    """Counts arrivals and turn endings for every square.

    landings counts every arrival, including ones the token leaves again
    straight away by drawing a card or being sent to jail. endings counts where
    the turn actually finished, so it adds up to the turn count.
    """

    def __init__(self):
        self.landings = [0] * BOARD_SIZE
        self.endings = [0] * BOARD_SIZE
        self.jailLandings = 0
        self.jailEndings = 0
        self.dice = {total: 0 for total in range(2, 13)}

    def recordLanding(self, space, jailed=False):
        self.landings[space] += 1
        if jailed:
            self.jailLandings += 1

    def recordEnding(self, space, jailed=False):
        self.endings[space] += 1
        if jailed:
            self.jailEndings += 1

    def boardFrame(self):
        landings = self.landings + [self.landings[JAIL] - self.jailLandings,
                                    self.jailLandings]
        endings = self.endings + [self.endings[JAIL] - self.jailEndings,
                                  self.jailEndings]
        return pd.DataFrame({
            "space": range(BOARD_SIZE + 2),
            "name": SPACE_NAMES,
            "landings": landings,
            "endings": endings,
        })

    def diceFrame(self):
        return pd.DataFrame({
            "value": list(self.dice),
            "frequency": list(self.dice.values()),
        })


def diceRoll(rng):
    #Return format: bool, total; bool indicates a double
    first = rng.randint(1, 6)
    second = rng.randint(1, 6)
    return first == second, first + second


def nearestAhead(position, targets):
    for step in range(1, BOARD_SIZE + 1):
        space = (position + step) % BOARD_SIZE
        if space in targets:
            return space
    raise ValueError(position)


def drawCard(position, deck, rng):
    #Return format: space, passed Go, sent to jail
    action, value = deck[rng.randrange(len(deck))]

    if action is None:
        return position, False, False

    if action == "jail":
        return JAIL, False, True

    if action == "advance":
        return value, value < position, False

    if action == "nearest":
        space = nearestAhead(position, targets=value)
        return space, space < position, False

    if action == "back":
        #Backwards past Go doesn't collect
        return (position - value) % BOARD_SIZE, False, False

    raise ValueError(action)


def moveAndResolve(position, roll, stats, rng):
    #Return format: space, laps, sent to jail
    laps = 0

    position += roll
    if position >= BOARD_SIZE:
        position -= BOARD_SIZE
        laps += 1
    stats.recordLanding(position)

    #A Chance card can drop you on Community Chest (36 back 3 -> 33)
    for _ in range(3):
        if position == GO_TO_JAIL:
            stats.recordLanding(JAIL, jailed=True)
            return JAIL, laps, True

        if position in CHANCE_SPACES:
            deck = CHANCE_DECK
        elif position in CHEST_SPACES:
            deck = CHEST_DECK
        else:
            break

        space, passedGo, jailed = drawCard(position, deck, rng)
        if jailed:
            stats.recordLanding(JAIL, jailed=True)
            return JAIL, laps, True
        if space == position:
            break

        position = space
        if passedGo:
            laps += 1
        stats.recordLanding(position)

    return position, laps, False


def runSimulation(targetRounds, rng):
    stats = Stats()
    position = GO
    inJail = False
    jailTurns = 0
    doublesRun = 0
    roundCount = 0
    turnCount = 0

    while roundCount < targetRounds:
        turnCount += 1
        doubles, roll = diceRoll(rng)
        stats.dice[roll] += 1

        if inJail:
            doublesRun = 0
            if doubles:
                inJail = False
                jailTurns = 0
            else:
                jailTurns += 1
                if jailTurns < 3:
                    stats.recordEnding(JAIL, jailed=True)
                    continue
                #Third failed try: pay the fine and move on this same roll
                inJail = False
                jailTurns = 0
            position, laps, inJail = moveAndResolve(JAIL, roll, stats, rng)
            roundCount += laps
            stats.recordEnding(position, inJail)
            continue

        if doubles:
            doublesRun += 1
            if doublesRun == 3:
                doublesRun = 0
                position = JAIL
                inJail = True
                jailTurns = 0
                stats.recordLanding(JAIL, jailed=True)
                stats.recordEnding(JAIL, jailed=True)
                continue
        else:
            doublesRun = 0

        position, laps, inJail = moveAndResolve(position, roll, stats, rng)
        roundCount += laps
        stats.recordEnding(position, inJail)
        if inJail:
            #Getting jailed ends the turn, so the doubles run ends too
            jailTurns = 0
            doublesRun = 0

    return stats, roundCount, turnCount


def main():
    parser = argparse.ArgumentParser(description="Simulate Monopoly square frequencies.")
    parser.add_argument("rounds", type=int, help="how many times to pass Go before stopping")
    parser.add_argument("--seed", type=int, default=None, help="seed for a repeatable run")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    if args.rounds < 1:
        parser.error("rounds must be at least 1")

    outputDir = args.output_dir or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "Analyze")
    os.makedirs(outputDir, exist_ok=True)

    rng = random.Random(args.seed)
    stats, roundCount, turnCount = runSimulation(args.rounds, rng)

    print("----Simulation Complete----")
    if args.seed is not None:
        print("Seed:", args.seed)
    print("Rounds:", roundCount)
    print("Turns:", turnCount)
    print("Jailings:", stats.jailLandings,
          f"({100 * stats.jailLandings / turnCount:.2f}% of turns)")
    print("Turns spent in jail:", stats.jailEndings,
          f"({100 * stats.jailEndings / turnCount:.2f}% of turns)")

    suffix = f"{roundCount}_rounds_{turnCount}_turns.csv"
    boardPath = os.path.join(outputDir, f"gameBoard_Results_{suffix}")
    dicePath = os.path.join(outputDir, f"diceRoll_Results_{suffix}")

    print("Exporting Game Board Data")
    stats.boardFrame().to_csv(boardPath, index=False)
    print("Exporting Dice Roll Data")
    stats.diceFrame().to_csv(dicePath, index=False)


if __name__ == "__main__":
    sys.exit(main())
