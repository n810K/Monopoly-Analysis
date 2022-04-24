from multiprocessing.dummy import current_process
import sys
import random
import pandas as pd
import os
#40 Squares in Monopoly

def chanceSpace(currentPosition):
    #Return Format: bool, space; bool to indicate whether sent to jail
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
    Chance Spots: 7,22,36 
    """
    updatedPosition = currentPosition
    movementCards = {1 : 0, 2 : 24, 3 : 11, 4 : 39}
    chanceCard = random.randint(1,16)

    if chanceCard <= 4:
        updatedPosition = movementCards[chanceCard]

    elif chanceCard == 5:
        updatedPosition = 10
        return True, updatedPosition #Sent to Jail

    elif chanceCard == 6:
        #print("Chance Card: Move back 3 Spaces")
        updatedPosition = currentPosition - 3

    #Advance to nearest utility
    elif chanceCard == 7: 
        if (currentPosition > 12 and currentPosition < 28):
            updatedPosition = 28

        elif (currentPosition > 28 or currentPosition < 12):
            updatedPosition = 12

    elif chanceCard == 8:
        #print("Chance Card: Advance to Nearest Railroad")
        if (currentPosition > 5 and currentPosition < 15):
            updatedPosition = 15
            #print("Updated Position:", globalPosition)
        elif (currentPosition > 15 and currentPosition < 25):
            updatedPosition = 25
            #print("Updated Position:", globalPosition)
        elif (currentPosition > 25 and currentPosition < 35):
            updatedPosition = 35
            #print("Updated Position:", globalPosition)
        elif (currentPosition > 35 or currentPosition < 5):
            updatedPosition = 5
            #print("Updated Position:", globalPosition)
    return False, updatedPosition
    

def chestSpace(currentPosition):
    """
    Movement Cards:
    1) Advance to GO (0)
    2) Go to Jail (10)

    There are 16 different Community Chest Cards
    Chest Spots: 2, 17, 33
    """
    updatedPosition = currentPosition
    communityCard = random.randint(1,16)

    if communityCard == 1:
        #print("Chest Card: Advance to GO")
        updatedPosition = 0

    elif communityCard == 2: #Jail Chest Card
        updatedPosition = 10
        return True, updatedPosition #Indicate sent to jail
    return False, updatedPosition

def diceRoll():
    equalDice = False
    diceOne = random.randint(1,6)
    diceTwo = random.randint(1,6)
    #print("diceRolls:", diceOne, diceTwo)
    if diceOne == diceTwo:
        equalDice = True # double is true 
    return (equalDice, (diceOne + diceTwo))

def boardDictionarySetup():
    boardSpaces = {}
    for i in range(40): #Space 41 [index 40] will be IN jail 
        boardSpaces[i] = 0
    return boardSpaces

def diceRollStatisticsSetup():
    diceRollStats = {}
    for i in range(13):
        diceRollStats[i] = 0
    return diceRollStats

if __name__ == "__main__":
    boardStats = boardDictionarySetup()
    diceStats = diceRollStatisticsSetup()
    globalPosition = 0
    roundCount = 0
    turnCount = 0
    inJailCount = 0
    tripleDoubles = [False, False, False]
    
    # print(gameBoard)

    if len(sys.argv) <= 1:
        print("[ERROR]: Missing Simulation count in command line.\n          Format: ./monopoly.py <simulation count>")
        quit()

    simulationCount = int(sys.argv[1])
    


    while (roundCount < simulationCount):
        jailFlag = False
        equalFlag, rollResult = diceRoll()
        diceStats[rollResult] += 1
        tripleDoubles[turnCount%3] = equalFlag

        if (tripleDoubles[0] == True and len(set(tripleDoubles)) == 1):
            globalPosition = 10
            inJailCount += 1
            for i in range(3):
                equalFlag, rollResult = diceRoll()
                if (equalFlag == True):
                    break
            if (equalFlag == False):
                equalFlag, rollResult = diceRoll()
            globalPosition += rollResult
        
        globalPosition += rollResult

        if (globalPosition > 39):
            globalPosition = globalPosition%40
            roundCount += 1
        
        boardStats[globalPosition] += 1

        if (globalPosition == 7 or globalPosition == 22 or globalPosition == 36): #Chance Cards
            currentPosition = globalPosition
            jailFlag, updatedPosition = chanceSpace(globalPosition)
            if (currentPosition != updatedPosition):
                globalPosition = updatedPosition
                if (jailFlag == False):
                    boardStats[globalPosition] += 1


        if (globalPosition == 2 or globalPosition == 17 or globalPosition == 33): #Chest Cards
            currentPosition = globalPosition
            jailFlag, updatedPosition = chestSpace(globalPosition)
            if (currentPosition != updatedPosition):
                globalPosition = updatedPosition
                if (jailFlag == False):
                    boardStats[globalPosition] += 1
        
        if (globalPosition == 30):
            globalPosition = 10
            inJailCount += 1
            jailFlag = True
        
        turnCount += 1

        if (jailFlag == True):
            for i in range(3):
                equalFlag, rollResult = diceRoll()
                if (equalFlag == True):
                    break
            if (equalFlag == False):
                equalFlag, rollResult = diceRoll()
            globalPosition += rollResult     
            boardStats[globalPosition] += 1      

    print("----Simulation Complete----")
    print("Turns:", turnCount)
    print("Game Board Spread:", boardStats)
    print("Dice Roll Spread", diceStats)

    #Track number of times jail visits were as "inmates"
    visitCount = boardStats[10]
    boardStats[10] = visitCount + inJailCount
    boardStats[40] = visitCount 
    boardStats[41] = inJailCount

    if not os.path.exists('Results'):
        os.mkdir("Results")

    print("Exporting Game Board Data")
    (pd.DataFrame.from_dict(data=boardStats, orient='index').to_csv(f'gameBoard_Results_{simulationCount}_rounds_{turnCount}_turns.csv', header=False))
    print("Exporting Dice Roll Data")
    (pd.DataFrame.from_dict(data=diceStats, orient='index').to_csv(f'diceRoll_Results_{simulationCount}_rounds_{turnCount}_turns.csv', header=False))
    