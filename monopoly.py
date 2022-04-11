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
    print(movementCards[1])
    chanceCard = 7 #random.randint(1,16)
    print(chanceCard)

    
    

    if chanceCard < 6:
        globalPosition = movementCards[chanceCard]
    elif chanceCard == 6:
        globalPosition -= 3
    elif chanceCard == 7:
        #Need to find a way to move to the next position, same with railroad
    elif chanceCard == 8:
        nearestRailroad = min(5-globalPosition, 15-globalPosition, 25-globalPosition, 35-globalPosition)
        globalPosition = nearestRailroad

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

def diceRoll():
    # diceOne = 
    # diceTwo = 
    return 

if __name__ == "__main__":
    globalPosition = 13
    chanceSpace()