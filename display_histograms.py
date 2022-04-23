import os
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

#== Global Variables ==#
DEBUG = {               #turn off debugging outputs
            "global": 0,
            "read": 1,


        }   

PATH = os.getcwd()
SIMCOUNT = 100

if DEBUG["global"]:
    print(f"PATH: {PATH}")


#== read diceRoll and gameBoard results ==#
diceRoll = pd.read_csv(os.path.join(PATH, f"diceRoll_Results_{SIMCOUNT}_rounds.csv"), names=["value","frequency"])

gameBoard = pd.read_csv(os.path.join(PATH, f"gameBoard_Results_{SIMCOUNT}_rounds.csv"), names=["space","frequency"])

if DEBUG["read"]:
    print(diceRoll)
    print('\n')
    print(gameBoard)

#=========================================#

#== generate histogram ==#
#= seaborn/matplotlib settings =#
sns.set(style="darkgrid")
#===============================#

turnCount = diceRoll["frequency"].sum()


plt.bar(diceRoll["value"], diceRoll["frequency"])
plt.title(f"Dice Rolls after {turnCount} turns")
plt.xticks(range(0,13,1))
plt.show()