"""Checks on the simulation. Run with `python3 test_monopoly.py` or pytest."""

import random
import sys

import monopoly as m

SEED = 20260809
ROUNDS = 60000

#Long-run share of turn endings from published analyses of the long-jail model.
#Jail isn't in here on purpose: sources disagree on whether the turn you get
#sent to jail counts as time served, so it isn't comparable.
REFERENCE = {
    24: 2.99,   # Illinois
    0: 2.91,    # Go
    25: 2.87,   # B&O
    20: 2.82,   # Free Parking
    18: 2.82,   # Tennessee
    19: 2.81,   # New York
}
TOLERANCE = 0.12   # percentage points, roughly 4 sd at this sample size

_run = None


def sim():
    #One shared run so the statistical checks all agree with each other
    global _run
    if _run is None:
        _run = m.runSimulation(ROUNDS, random.Random(SEED))
    return _run


def test_deck_sizes():
    assert len(m.CHANCE_DECK) == 16
    assert len(m.CHEST_DECK) == 16


def test_chance_movement_cards():
    movers = [c for c in m.CHANCE_DECK if c[0] is not None]
    assert len(movers) == 10
    assert sum(1 for a, v in movers if a == "nearest" and v == m.RAILROADS) == 2
    assert ("advance", 5) in movers          # ride on the Reading


def test_chest_movement_cards():
    movers = [c for c in m.CHEST_DECK if c[0] is not None]
    assert set(movers) == {("advance", m.GO), ("jail", None)}


def test_nearest_ahead():
    assert m.nearestAhead(7, m.RAILROADS) == 15
    assert m.nearestAhead(22, m.RAILROADS) == 25
    assert m.nearestAhead(36, m.RAILROADS) == 5
    assert m.nearestAhead(7, m.UTILITIES) == 12
    assert m.nearestAhead(22, m.UTILITIES) == 28
    assert m.nearestAhead(36, m.UTILITIES) == 12
    assert m.nearestAhead(12, m.UTILITIES) == 28    # standing on one moves you to the next


def test_passing_go():
    def draw(position, card):
        return m.drawCard(position, [card], random.Random(0))

    assert draw(36, ("advance", m.GO)) == (0, True, False)
    assert draw(36, ("advance", 24)) == (24, True, False)
    assert draw(7, ("advance", 24)) == (24, False, False)
    assert draw(36, ("nearest", m.RAILROADS)) == (5, True, False)
    assert draw(7, ("nearest", m.RAILROADS)) == (15, False, False)
    assert draw(1, ("back", 3)) == (38, False, False)
    assert draw(36, ("back", 3)) == (33, False, False)
    assert draw(36, ("jail", None)) == (m.JAIL, False, True)
    assert draw(22, (None, None)) == (22, False, False)


def test_two_dice():
    rng = random.Random(1)
    for _ in range(2000):
        doubles, total = m.diceRoll(rng)
        assert 2 <= total <= 12
        if doubles:
            assert total % 2 == 0


def test_one_ending_per_turn():
    stats, _, turns = sim()
    assert sum(stats.endings) == turns


def test_landings_at_least_turns():
    stats, _, turns = sim()
    assert sum(stats.landings) >= turns


def test_nothing_ends_on_go_to_jail():
    stats, _, _ = sim()
    assert stats.endings[m.GO_TO_JAIL] == 0
    assert stats.landings[m.GO_TO_JAIL] > 0


def test_jail_rows_add_up():
    stats, _, _ = sim()
    board = stats.boardFrame()
    for column in ("landings", "endings"):
        total = board.loc[m.JAIL, column]
        visiting = board.loc[m.JUST_VISITING, column]
        inmates = board.loc[m.IN_JAIL, column]
        assert total == visiting + inmates
        assert visiting > 0 and inmates > 0


def test_frame_shape():
    stats, _, _ = sim()
    board = stats.boardFrame()
    assert len(board) == m.BOARD_SIZE + 2
    assert list(board["name"]) == m.SPACE_NAMES


def test_seed_repeats():
    a = m.runSimulation(300, random.Random(7))
    b = m.runSimulation(300, random.Random(7))
    assert a[1:] == b[1:]
    assert a[0].endings == b[0].endings
    assert a[0].landings == b[0].landings
    assert a[0].dice == b[0].dice


def test_rounds_target_met():
    _, rounds, _ = sim()
    assert rounds >= ROUNDS


def test_dice_are_fair():
    stats, _, turns = sim()
    assert sum(stats.dice.values()) == turns
    mean = sum(v * n for v, n in stats.dice.items()) / turns
    assert abs(mean - 7.0) < 0.05, mean
    for value, count in stats.dice.items():
        expected = turns * (6 - abs(value - 7)) / 36
        assert abs(count - expected) < 0.12 * expected, (value, count, expected)


def test_jail_is_busiest():
    stats, _, _ = sim()
    assert stats.endings.index(max(stats.endings)) == m.JAIL


def test_time_served():
    #Per jailing: the turn you arrive, plus one per failed attempt.
    #1 + 5/6 + (5/6)^2 = 2.528
    stats, _, _ = sim()
    ratio = stats.jailEndings / stats.jailLandings
    assert abs(ratio - 2.528) < 0.06, ratio


def test_illinois_near_the_top():
    #Illinois only beats Go by about 0.07 points, so allow either at the top
    stats, _, _ = sim()
    ranked = sorted(range(m.BOARD_SIZE), key=lambda s: stats.endings[s], reverse=True)
    assert ranked[0] == m.JAIL
    assert 24 in ranked[1:4]


def test_matches_published_numbers():
    stats, _, turns = sim()
    for space, expected in REFERENCE.items():
        actual = 100 * stats.endings[space] / turns
        assert abs(actual - expected) < TOLERANCE, (m.SPACE_NAMES[space], actual, expected)


def test_railroads_above_average():
    stats, _, turns = sim()
    average = turns / m.BOARD_SIZE
    for railroad in m.RAILROADS:
        if railroad == 35:
            continue    # nothing points at Short Line, it sits below average
        assert stats.endings[railroad] > average, railroad


def test_chance_and_chest_are_low():
    #10 of the 16 Chance cards move you straight off again
    stats, _, turns = sim()
    average = turns / m.BOARD_SIZE
    for space in m.CHANCE_SPACES:
        assert stats.endings[space] < 0.6 * average
        assert stats.landings[space] > stats.endings[space]


def main():
    tests = [(name, fn) for name, fn in sorted(globals().items())
             if name.startswith("test_") and callable(fn)]
    failed = 0
    for name, fn in tests:
        try:
            fn()
        except AssertionError as exc:
            failed += 1
            print(f"FAIL {name}: {exc}")
        else:
            print(f"ok   {name}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
