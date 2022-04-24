import os
import re
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

#== Global Variables ==#
DEBUG = {               #turn off debugging outputs
            "global": 0,
            "read": 1,
            "histogram": 0,


        }   

PATH = os.getcwd()
SIMCOUNT = 100

if DEBUG["global"]:
    print(f"PATH: {PATH}")


#== read diceRoll and gameBoard results ==# 
csv_files = list(filter(lambda f: f.endswith('.csv'), os.listdir(PATH)))

diceRollFile = None
gameBoardFile = None

for file in csv_files:
    if (diceRollFile == None) and ("diceRoll_Results" in file) and (str(SIMCOUNT) in file):
        diceRollFile = file

    elif (gameBoardFile == None) and ("gameBoard_Results" in file) and (str(SIMCOUNT) in file):
        gameBoardFile = file

diceRoll = pd.read_csv(os.path.join(PATH, diceRollFile), names=["value","frequency"])
gameBoard = pd.read_csv(os.path.join(PATH, gameBoardFile), names=["space","frequency"])

if DEBUG["read"]:
    print(diceRollFile)
    print(gameBoardFile)
    print('\n')
    print(diceRoll)
    print('\n')
    print(gameBoard)

#=========================================#


#== seaborn/matplotlib settings ==#
sns.set(style="darkgrid")

#=================================#


#== generate dice roll histogram ==#
# assuming filenames -> type_results_x_rounds_x_turns.csv
turnsCount = file.split(".")[0].split("_")[4]

if DEBUG["histogram"]:
    print(f"turnCountDice: {turnCountDice}, turnCountSpace: {turnCountSpace}")


plt.bar(diceRoll["value"], diceRoll["frequency"])
plt.title(f"Dice Rolls after {turnsCount} turns")
plt.xticks(range(0,13,1))
plt.show()


