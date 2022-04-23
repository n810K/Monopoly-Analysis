import random
import pandas as pd
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
    #Chance Spots: 7,22,36 
    global globalPosition

    movementCards = {1 : 0, 2 : 24, 3 : 11, 4 : 39}
    chanceCard = random.randint(1,16)
    #print("Chance Random Roll:", chanceCard) # Print selected chance card's index

    if chanceCard < 5:
        #print("Chance Card: Move to board index", movementCards[chanceCard])
        globalPosition = movementCards[chanceCard]

    elif chanceCard == 5:
        #print("Chance: Go to Jail")
        globalPosition = 10
        #print("Updated Position:", globalPosition)
        return True

    elif chanceCard == 6:
        #print("Chance Card: Move back 3 Spaces")
        globalPosition -= 3

    elif chanceCard == 7:
        #print("Chance Card: Advance to Nearest Utility")
        if (globalPosition > 12 and globalPosition < 28):
            globalPosition = 28
            #print("Updated Position:", globalPosition)
            return 1
        elif (globalPosition > 28 or globalPosition < 12):
            globalPosition = 12
            #print("Updated Position:", globalPosition)
            return 1

    elif chanceCard == 8:
        #print("Chance Card: Advance to Nearest Railroad")
        if (globalPosition > 5 and globalPosition < 15):
            globalPosition = 15
            #print("Updated Position:", globalPosition)
            return 1
        elif (globalPosition > 15 and globalPosition < 25):
            globalPosition = 25
            #print("Updated Position:", globalPosition)
            return 1
        elif (globalPosition > 25 and globalPosition < 35):
            globalPosition = 35
            #print("Updated Position:", globalPosition)
            return 1
        elif (globalPosition > 35 or globalPosition < 5):
            globalPosition = 5
            #print("Updated Position:", globalPosition)
            return 1

    

def chestSpace():
    """
    Movement Cards:
    1) Advance to GO (0)
    2) Go to Jail (10)

    There are 16 different Community Chest Cards
    """
    #Chest Spots: 2, 17, 33
    global globalPosition
    communityCard = random.randint(1,16)

    if communityCard == 1:
        #print("Chest Card: Advance to GO")
        globalPosition = 0
    elif communityCard == 2:
        #print("Chest Card: Go to Jail")
        globalPosition = 10
        #print("Updated Position:", globalPosition)
        return True #Indicate sent to jail
    
    #print("Updated Position:", globalPosition)

def diceRoll():
    diceOne = random.randint(1,6)
    diceTwo = random.randint(1,6)
    #print("diceRolls:", diceOne, diceTwo)
    equalDice = False
    if diceOne == diceTwo:
        equalDice = True # double is true 
    return (equalDice, (diceOne + diceTwo))

def boardDictionarySetup():
    boardSpaces = {}
    for i in range(40): #Space 41 will be IN jail 
        boardSpaces[i] = 0
    return boardSpaces

def diceRollStatisticsSetup():
    diceRollStats = {}
    for i in range(13):
        diceRollStats[i] = 0
    return diceRollStats

if __name__ == "__main__":
    gameBoard = boardDictionarySetup()
    diceRollStats = diceRollStatisticsSetup()
    globalPosition = 0
    roundCount = 0
    turnCount = 0
    inJailCount = 0
    tripleDoubles = [False, False, False]
    
    print(gameBoard)

    simulationCount = int(input("How many rounds should we simulate? (Go-Go is 1 Round): "))
    while (roundCount < simulationCount):
        chanceResult = False
        chestResult = False
        equalFlag, rollResult = diceRoll()

        globalPosition += rollResult
        #print("Position After Roll:", globalPosition)
        if (globalPosition >= 40):
            globalPosition = globalPosition%40
            roundCount += 1

        turnCount += 1

        diceRollStats[rollResult] += 1
        gameBoard[globalPosition] += 1

        tripleDoubles[turnCount%3] = equalFlag

        #print(tripleDoubles)
        
        if (globalPosition == 7 or globalPosition == 22 or globalPosition == 36):
            #print("Landed on Chance")
            chanceResult = chanceSpace()
            gameBoard[globalPosition] += 1

        if (globalPosition == 2 or globalPosition == 17 or globalPosition == 33):
            #print("Landed on Community Chest")
            chestResult = chestSpace()
            gameBoard[globalPosition] += 1

        if ((tripleDoubles[0] == True and len(set(tripleDoubles)) == 1) or chanceResult == True): #Check that all items in the list are True
            #print("Rolling from Jail")
            inJailCount += 1
            globalPosition = 10 # Move to jail since rolling 3 doubles in a row is speeding
            for i in range(3):
                equalFlag, rollResult = diceRoll()
                turnCount += 1
                #print("Jail Roll", i, "", equalFlag)
                if equalFlag == True:
                    globalPosition += rollResult
                    break

    print("----Simulation Complete----")
    print("Turns:", turnCount)
    print("Game Board Spread:", gameBoard)
    print("Dice Roll Spread", diceRollStats)
    print("Exporting Game Board Data")

    #Track number of times jail visits were as "inmates"
    gameBoard[40] = inJailCount 

    (pd.DataFrame.from_dict(data=gameBoard, orient='index').to_csv(f'gameBoard_Results_{simulationCount}_rounds.csv', header=False))
    print("Exporting Dice Roll Data")
    (pd.DataFrame.from_dict(data=diceRollStats, orient='index').to_csv(f'diceRoll_Results_{simulationCount}_rounds.csv', header=False))
    