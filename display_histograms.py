import sys
import os
import re
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

#== Global Variables ==#
DEBUG = {               #turn off debugging outputs
            "global": 0,
            "read": 0,
            "histogram": 0,


        }   

PATH = os.getcwd()

if len(sys.argv) <= 1:
    print("[ERROR]: Missing Simulation count in command line.\n          Format: ./display_histograms.py <simulation count>")
    quit()

SIMCOUNT = int(sys.argv[1])

labels = [
            "Go",
            "Medit.",
            "C. Chest (0)",
            "Baltic",
            "I. Tax",
            "R. Railroad",
            "Oriental",
            "Chance (0)",
            "Vermont",
            "Connecticut",
            "Just Visiting",
            "St. Charles",
            "Electric Company",
            "States",
            "Virginia",
            "Pennsylvania Railroad",
            "St. James",
            "Community Chest (1)",
            "Tennessee",
            "New York",
            "Free Parking",
            "Kentucky",
            "Chance (1)",
            "Indiana",
            "Illinois",
            "B. & O. Railroad",
            "Atlantic",
            "Ventnor",
            "Water Works",
            "Marvin Gardens",
            "Go to Jail",
            "Pacific",
            "North Carolina",
            "Community Chest (2)",
            "Pennsylvania",
            "Short Line",
            "Chance (2)",
            "Park Place",
            "Luxury Tax",
            "Boardwalk",
            "In Jail"
         ]



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

gameBoard.insert(0, "name", labels)

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
    print(f"turnsCount: {turnsCount}")

fig, (ax1, ax2) = plt.subplots(2)


ax1.bar(diceRoll["value"], diceRoll["frequency"])
ax1.set_title("Dice Rolls")
ax1.set_xticklabels(range(0,13,1))

#== generate game board histogram ==#


ax2.bar(gameBoard["space"], gameBoard["frequency"])
ax2.set_title("Spaces")
ax2.set_xticks(range(0,41,1))
ax2.set_xticklabels(gameBoard["name"], rotation=-90, fontsize=6)
fig.suptitle(f"Frequencies After {turnsCount} Turns")

fig.set_size_inches(14, 9)
plt.show()