import sys
import os
import re
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

#== Global Variables ==#
DEBUG = {               #turn off debugging outputs
            "global": 1,
            "read": 1,
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
            "Jail + Visiting", #Just Visiting
            "St. Charles",
            "El. Company",
            "States",
            "Virginia",
            "Penns Railroad",
            "St. James",
            "C. Chest (1)",
            "Tennessee",
            "New York",
            "Free Parking",
            "Kentucky",
            "Chance (1)",
            "Indiana",
            "Illinois",
            "B&O Railroad",
            "Atlantic",
            "Ventnor",
            "Water Works",
            "Marvin Gardens",
            "Go to Jail",
            "Pacific",
            "North Carolina",
            "C. Chest (2)",
            "Pennsylvania",
            "Short Line",
            "Chance (2)",
            "Park Place",
            "Luxury Tax",
            "Boardwalk",
            "Just Visiting",
            "In Jail"
         ]



if DEBUG["global"]:
    print(f"PATH: {PATH}")


#== read diceRoll and gameBoard results ==# 
analyse_dir = os.path.join(PATH, "Analyze")
csv_files = list(filter(lambda f: f.endswith('.csv'), os.listdir(analyse_dir)))

diceRollFile = None
gameBoardFile = None

simCountString = f"_{SIMCOUNT}_"

for file in csv_files:
    if (diceRollFile == None) and ("diceRoll_Results" in file) and (simCountString in file):
        diceRollFile = file

    elif (gameBoardFile == None) and ("gameBoard_Results" in file) and (simCountString in file):
        gameBoardFile = file

if not diceRollFile:
    print("diceRollFile not found")
    quit()

if not gameBoardFile:
    print("gameBoardFile not found")
    quit()

diceRoll = pd.read_csv(os.path.join(analyse_dir, diceRollFile), names=["value","frequency"])
gameBoard = pd.read_csv(os.path.join(analyse_dir, gameBoardFile), names=["space","frequency"])

gameBoard.insert(0, "name", labels)

if DEBUG["read"]:
    print(analyse_dir)
    print(csv_files)
    print(diceRollFile)
    print(gameBoardFile)
    print(diceRoll)
    print(gameBoard)

#=========================================#


#== seaborn/matplotlib settings ==#
sns.set(style="darkgrid")

#=================================#


#== generate dice roll histogram ==#
# assuming filenames -> type_results_x_rounds_x_turns.csv
turnsCount = file.split(".")[0].split("_")[4]
roundsCount = file.split(".")[0].split("_")[2]

if DEBUG["histogram"]:
    print(f"turnsCount: {turnsCount}")

fig, (ax1, ax2) = plt.subplots(2)


ax1.bar(diceRoll["value"], diceRoll["frequency"])
ax1.set_title("Dice Rolls")
ax1.set_xticks(range(0,13,1))
ax1.set_xticklabels(range(0,13,1))

#== generate game board histogram ==#


ax2.bar(gameBoard["space"], gameBoard["frequency"])
ax2.set_title("Spaces")
ax2.set_xticks(range(0,42,1))
ax2.set_xticklabels(gameBoard["name"], rotation=-90, fontsize=8)
fig.suptitle(f"Frequencies After {turnsCount} Turns")

fig.set_size_inches(14, 9)

if not os.path.exists('Results'):
    os.mkdir("Results")

plt.savefig(f"Results/Monopoly Analysis Results - {roundsCount}.png")

plt.show()

