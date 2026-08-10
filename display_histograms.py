import argparse
import os
import sys

import matplotlib

#Pick the backend before pyplot loads, otherwise --no-show still needs a display
if "--no-show" in sys.argv:
    matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Rectangle

PATH = os.path.dirname(os.path.abspath(__file__))

SURFACE = "#fcfcfb"
TEXT_PRIMARY = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
GRID = "#dedcd5"
ENDINGS_COLOUR = "#2a78d6"
LANDINGS_COLOUR = "#eb6834"
NEUTRAL = "#e4e2db"

RAMP = LinearSegmentedColormap.from_list("board", [
    "#f4f8fd", "#dbe9f8", "#b7d2f0", "#8ab5e6",
    "#5b95db", "#2a78d6", "#1f5da8", "#15427a",
])

BOARD_COLUMNS = ["space", "name", "landings", "endings"]
BOARD_SIZE = 40
JAIL = 10
GO_TO_JAIL = 30
JUST_VISITING = 40
IN_JAIL = 41

#Short enough to fit inside a heatmap cell
SHORT_NAMES = [
    "Go", "Medit.", "Chest", "Baltic", "Inc. Tax",
    "Reading", "Oriental", "Chance", "Vermont", "Connect.",
    "JAIL", "St. Chas.", "Electric", "States", "Virginia",
    "Penn. RR", "St. James", "Chest", "Tennes.", "New York",
    "Free Pk.", "Kentucky", "Chance", "Indiana", "Illinois",
    "B&O RR", "Atlantic", "Ventnor", "Water Wks", "Marvin",
    "Go->Jail", "Pacific", "N. Carol.", "Chest", "Penn. Ave",
    "Short Ln", "Chance", "Park Pl.", "Lux. Tax", "Boardwlk",
]

GRID_SIDE = 11


def boardCell(space):
    #Grid row/col for a square, Go bottom right like the real board
    if space <= 10:
        return 10, 10 - space
    if space <= 20:
        return 20 - space, 0
    if space <= 30:
        return 0, space - 20
    return space - 30, 10


def findResults(analyzeDir, rounds):
    if not os.path.isdir(analyzeDir):
        sys.exit(f"[ERROR]: no Analyze directory at {analyzeDir}. Run monopoly.py first.")

    marker = f"_{rounds}_rounds_"
    csvFiles = [f for f in os.listdir(analyzeDir)
                if f.endswith(".csv") and marker in f]

    def newest(prefix):
        matches = [f for f in csvFiles if f.startswith(prefix)]
        if not matches:
            return None
        #Runs can share a round count but differ in turns, so take the latest
        return max(matches, key=lambda f: os.path.getmtime(os.path.join(analyzeDir, f)))

    diceRollFile = newest("diceRoll_Results_")
    gameBoardFile = newest("gameBoard_Results_")

    if not diceRollFile:
        sys.exit(f"[ERROR]: no diceRoll_Results_*{marker}*.csv in {analyzeDir}")
    if not gameBoardFile:
        sys.exit(f"[ERROR]: no gameBoard_Results_*{marker}*.csv in {analyzeDir}")
    return diceRollFile, gameBoardFile


def parseCounts(filename):
    #filenames look like type_Results_x_rounds_x_turns.csv
    parts = os.path.splitext(filename)[0].split("_")
    try:
        return parts[parts.index("rounds") - 1], parts[parts.index("turns") - 1]
    except ValueError:
        sys.exit(f"[ERROR]: cannot read round/turn counts from {filename!r}")


def loadBoard(path):
    board = pd.read_csv(path)
    missing = [c for c in BOARD_COLUMNS if c not in board.columns]
    if missing:
        sys.exit(f"[ERROR]: {os.path.basename(path)} is missing {missing}. It was "
                 f"probably written by an older monopoly.py, so re-run the sim.")
    return board


def styleAxes(ax):
    ax.set_facecolor(SURFACE)
    ax.set_axisbelow(True)
    for edge in ("top", "right", "left"):
        ax.spines[edge].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=TEXT_SECONDARY, length=0)


def plotBoardMap(ax, pct):
    #Jail is four times any other square, so keep it off the colour scale
    others = [p for s, p in enumerate(pct) if s not in (JAIL, GO_TO_JAIL)]
    norm = Normalize(vmin=min(others), vmax=max(others))

    for space, share in enumerate(pct):
        row, col = boardCell(space)
        x, y = col, GRID_SIDE - 1 - row

        if space == GO_TO_JAIL:
            #Zero because no turn can end here, which isn't the same as cold
            face, ink = NEUTRAL, TEXT_SECONDARY
        else:
            shade = norm(min(share, norm.vmax))
            face = RAMP(shade)
            ink = "#ffffff" if shade > 0.55 else TEXT_PRIMARY

        ax.add_patch(Rectangle((x + 0.02, y + 0.02), 0.96, 0.96,
                               facecolor=face, edgecolor=SURFACE, linewidth=1.5))
        ax.text(x + 0.5, y + 0.64, SHORT_NAMES[space], ha="center", va="center",
                fontsize=5.0, color=ink)
        ax.text(x + 0.5, y + 0.36, f"{share:.2f}", ha="center", va="center",
                fontsize=7.2, weight="bold", color=ink)

    ax.text(0.5, 0.14, "off scale", ha="center", va="center",
            fontsize=4.6, color="#ffffff", style="italic")

    topShare, topSpace = max((p, s) for s, p in enumerate(pct)
                             if s not in (JAIL, GO_TO_JAIL))
    ax.text(5.5, 6.5, f"{pct[JAIL]:.1f}%", ha="center", va="center",
            fontsize=30, weight="bold", color=ENDINGS_COLOUR)
    ax.text(5.5, 5.75, "of turns end in Jail —\nfour times any other square",
            ha="center", va="center", fontsize=8, color=TEXT_PRIMARY, linespacing=1.5)
    ax.text(5.5, 4.6,
            f"Busiest property: {SHORT_NAMES[topSpace]} {topShare:.2f}%\n"
            f"Coldest: the Chance squares — 10 of their\n"
            f"16 cards move you straight back off",
            ha="center", va="center", fontsize=7, color=TEXT_SECONDARY, linespacing=1.6)

    ax.set_xlim(0, GRID_SIDE)
    ax.set_ylim(0, GRID_SIDE)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Where turns end, by board position  (% of turns)",
                 color=TEXT_PRIMARY, fontsize=11, loc="left", pad=10)

    bar = ax.inset_axes([0.30, -0.055, 0.42, 0.022])
    bar.imshow([list(range(256))], aspect="auto", cmap=RAMP)
    bar.set_xticks([0, 255])
    bar.set_xticklabels([f"{norm.vmin:.2f}%", f"{norm.vmax:.2f}%"],
                        fontsize=7, color=TEXT_SECONDARY)
    bar.set_yticks([])
    bar.tick_params(length=0)
    for spine in bar.spines.values():
        spine.set_visible(False)


def plotDice(ax, diceRoll):
    total = int(diceRoll["frequency"].sum())
    observed = [100 * f / total for f in diceRoll["frequency"]]
    expected = [100 * (6 - abs(v - 7)) / 36 for v in diceRoll["value"]]

    ax.bar(diceRoll["value"], observed, width=0.72, color=ENDINGS_COLOUR, label="Observed")
    ax.plot(diceRoll["value"], expected, linestyle="none", marker="_", markersize=11,
            markeredgewidth=2.4, color=LANDINGS_COLOUR, label="Fair-dice expectation")

    ax.set_title("Dice rolls  (% of rolls)", color=TEXT_PRIMARY, fontsize=11, loc="left")
    ax.set_xticks(range(2, 13))
    ax.set_xlabel("Roll total", color=TEXT_SECONDARY, fontsize=8)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8)
    styleAxes(ax)
    ax.legend(frameon=False, labelcolor=TEXT_SECONDARY, fontsize=8, loc="upper left")


def plotShares(ax, gameBoard, pct):
    ceiling = max(p for s, p in enumerate(pct) if s != JAIL) * 1.22
    colours = [NEUTRAL if s == GO_TO_JAIL else ENDINGS_COLOUR for s in range(BOARD_SIZE)]

    ax.bar(range(BOARD_SIZE), pct, width=0.68, color=colours)
    ax.set_ylim(0, ceiling)

    #Let jail run off the top instead of squashing the other 39 into a corner.
    #Baseline stays at zero so every other bar is still to scale.
    for offset in (0.0, 0.055):
        ax.plot([JAIL - 0.40, JAIL + 0.40],
                [ceiling * (0.86 + offset), ceiling * (0.90 + offset)],
                color=SURFACE, linewidth=2.4, solid_capstyle="butt",
                clip_on=False, zorder=3)
    ax.text(JAIL, ceiling * 0.985, f"{pct[JAIL]:.2f}%", ha="center", va="top",
            fontsize=8.5, weight="bold", color=TEXT_PRIMARY, zorder=4,
            bbox=dict(facecolor=SURFACE, edgecolor="none", pad=1.5))
    ax.annotate(f"{pct[GO_TO_JAIL]:.0f}%", xy=(GO_TO_JAIL, 0), xytext=(0, 4),
                textcoords="offset points", ha="center", fontsize=7, color=TEXT_SECONDARY)

    ax.set_title("Share of turn endings, every square  "
                 "(Go to Jail is 0 by definition — no turn can end there)",
                 color=TEXT_PRIMARY, fontsize=11, loc="left")
    ax.set_xticks(range(BOARD_SIZE))
    ax.set_xticklabels(gameBoard["name"][:BOARD_SIZE], rotation=-90, fontsize=7,
                       color=TEXT_SECONDARY)
    ax.set_ylabel("% of turns", color=TEXT_SECONDARY, fontsize=8)
    ax.set_xlim(-0.8, BOARD_SIZE - 0.2)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8)
    styleAxes(ax)


def plotDifferences(ax, gameBoard, turns):
    #Jail is left out and called out below instead: its gap is time served
    #rather than a card moving you on, and at 9%+ it flattens everything else.
    skip = {JAIL, JUST_VISITING, IN_JAIL}
    rows = [(name, landings, endings) for space, name, landings, endings
            in zip(gameBoard["space"], gameBoard["name"],
                   gameBoard["landings"], gameBoard["endings"])
            if landings != endings and space not in skip]
    rows.sort(key=lambda r: r[1], reverse=True)

    names = [name for name, _, _ in rows]
    landed = [100 * l / turns for _, l, _ in rows]
    ended = [100 * e / turns for _, _, e in rows]
    y = range(len(rows))
    height = 0.38

    ax.barh([i + height / 2 + 0.01 for i in y], landed, height=height,
            color=LANDINGS_COLOUR, label="Landed on")
    ax.barh([i - height / 2 - 0.01 for i in y], ended, height=height,
            color=ENDINGS_COLOUR, label="Turn ended there")

    for i, (l, e) in enumerate(zip(landed, ended)):
        ax.text(l + 0.06, i + height / 2 + 0.01, f"{l:.2f}", va="center",
                fontsize=7, color=TEXT_SECONDARY)
        ax.text(e + 0.06, i - height / 2 - 0.01, f"{e:.2f}", va="center",
                fontsize=7, color=TEXT_SECONDARY)

    ax.set_yticks(list(y))
    ax.set_yticklabels(names, fontsize=8, color=TEXT_SECONDARY)
    ax.invert_yaxis()
    ax.set_xlim(0, max(max(landed), max(ended)) * 1.55)
    ax.set_xlabel("% of turns", color=TEXT_SECONDARY, fontsize=8)

    bySpace = dict(zip(gameBoard["space"], zip(gameBoard["landings"], gameBoard["endings"])))
    jailed, served = bySpace[IN_JAIL]
    ax.text(0.985, 0.06,
            f"Jail works the other way round: entered on {100 * jailed / turns:.2f}% "
            f"of turns but occupied on {100 * served / turns:.2f}%\n"
            f"— about {served / jailed:.1f} turns served per sentence. "
            f"Left off this panel; it would flatten the card squares.",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=7.5,
            color=TEXT_SECONDARY, linespacing=1.5)

    ax.set_title("Landing on a square vs staying on it  "
                 "(only the squares where they differ)",
                 color=TEXT_PRIMARY, fontsize=11, loc="left")
    ax.xaxis.grid(True, color=GRID, linewidth=0.8)
    styleAxes(ax)
    ax.legend(frameon=False, labelcolor=TEXT_SECONDARY, fontsize=8,
              loc="upper right", bbox_to_anchor=(1.0, 0.98))


def main():
    parser = argparse.ArgumentParser(description="Plot Monopoly simulation results.")
    parser.add_argument("rounds", type=int, help="round count of the run to plot")
    parser.add_argument("--analyze-dir", default=os.path.join(PATH, "Analyze"))
    parser.add_argument("--results-dir", default=os.path.join(PATH, "Results"))
    parser.add_argument("--no-show", action="store_true", help="save the PNG only")
    args = parser.parse_args()

    diceRollFile, gameBoardFile = findResults(args.analyze_dir, args.rounds)
    rounds, _ = parseCounts(gameBoardFile)

    diceRoll = pd.read_csv(os.path.join(args.analyze_dir, diceRollFile))
    gameBoard = loadBoard(os.path.join(args.analyze_dir, gameBoardFile))

    squares = gameBoard[gameBoard["space"] < BOARD_SIZE]
    turns = int(squares["endings"].sum())
    pct = [100 * e / turns for e in squares["endings"]]

    fig = plt.figure(figsize=(15, 12.5), facecolor=SURFACE)
    gs = GridSpec(3, 2, figure=fig, height_ratios=[1.5, 0.78, 0.62],
                  width_ratios=[1.15, 1], hspace=0.42, wspace=0.20,
                  left=0.06, right=0.97, top=0.92, bottom=0.06)

    plotBoardMap(fig.add_subplot(gs[0, 0]), pct)
    plotDice(fig.add_subplot(gs[0, 1]), diceRoll)
    plotShares(fig.add_subplot(gs[1, :]), gameBoard, pct)
    plotDifferences(fig.add_subplot(gs[2, :]), gameBoard, turns)

    fig.suptitle(f"Monopoly board frequencies — {turns:,} turns ({int(rounds):,} rounds)",
                 color=TEXT_PRIMARY, fontsize=15, x=0.06, ha="left", y=0.965)

    os.makedirs(args.results_dir, exist_ok=True)
    outPath = os.path.join(args.results_dir, f"Monopoly Analysis Results - {rounds}.png")
    fig.savefig(outPath, dpi=130, facecolor=SURFACE)
    print("Saved", outPath)

    if not args.no_show:
        plt.show()


if __name__ == "__main__":
    sys.exit(main())
