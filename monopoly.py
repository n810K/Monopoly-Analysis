from glob import glob
import random
#40 Squares in Monopoly
def chanceSpace():
    """
    Movement Cards:
    1) Advance to Go (0)
    2) Advance to Illinois Avenue (24)
    3) Advance to St. Charles Palace (11)
    4) Advance to Boardwalk (39)
    5) Go to jail (10)
    6) Go back 3 spaces
    7) Advance to nearest Utility (12,28)
    8) Advance to nearest Railroad (5,15,25,35)
    
    There are 16 different Chance Cards
    """
    global globalPosition

    movementCards = {1 : 0, 2 : 24, 3 : 11, 4 : 39, 5 : 10}
    chanceCard = random.randint(1,16)
    print(chanceCard) # Print selected chance card's index

    if chanceCard < 6:
        print("Chance Card: Move to board index", movementCards[chanceCard])
        globalPosition = movementCards[chanceCard]

    elif chanceCard == 6:
        print("Chance Card: Move back 3 Spaces")
        globalPosition -= 3

    elif chanceCard == 7:
        print("Chance Card: Advance to Nearest Utility")
        if (globalPosition > 12 and globalPosition < 28):
            globalPosition = 28
            print("Between 12 and 28")
        elif (globalPosition > 28 or globalPosition < 12):
            globalPosition = 12
            print("Between 28 and 12")

    elif chanceCard == 8:
        print("Chance Card: Advance to Nearest Railroad")
        if (globalPosition > 5 and globalPosition < 15):
            globalPosition = 15
        elif (globalPosition > 15 and globalPosition < 25):
            globalPosition = 25
        elif (globalPosition > 25 and globalPosition < 35):
            globalPosition = 35
        elif (globalPosition > 35 or globalPosition < 5):
            globalPosition = 5

    print("Updated Position:", globalPosition)

def chestSpace():
    """
    Movement Cards:
    1) Advance to GO (0)
    2) Go to Jail (10)

    There are 16 different Community Chest Cards
    """
    global globalPosition
    communityCard = random.randint(1,16)

    if communityCard == 1:
        print("Chest Card: Advance to GO")
        globalPosition = 0
    elif communityCard == 2:
        print("Chest Card: Go to Jail")
        globalPosition = 10

def diceRoll():
    diceOne = random.randint(1,6)
    diceTwo = random.randint(1,6)
    return (diceOne + diceTwo)

if __name__ == "__main__":
    globalPosition = 0
    