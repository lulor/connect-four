from collections import Counter
import numpy as np
import math
import random

NUM_COLUMNS = 7
COLUMN_HEIGHT = 6
FOUR = 4
SYMBOLS = {1: "X", -1: "O", 0: "-"}


def valid_moves(board):
    """Returns columns where a disc may be played"""
    return [n for n in range(NUM_COLUMNS) if board[n, COLUMN_HEIGHT - 1] == 0]


def play(board, column, player):
    """Updates `board` as `player` drops a disc in `column`"""
    (index,) = next((i for i, v in np.ndenumerate(board[column]) if v == 0))
    board[column, index] = player


def take_back(board, column):
    """Updates `board` removing top disc from `column`"""
    (index,) = [i for i, v in np.ndenumerate(board[column]) if v != 0][-1]
    board[column, index] = 0


def four_in_a_row(board, player):
    """Checks if `player` has a 4-piece line"""
    return (
        any(
            all(board[c, r] == player)
            for c in range(NUM_COLUMNS)
            for r in (list(range(n, n + FOUR)) for n in range(COLUMN_HEIGHT - FOUR + 1))
        )
        or any(
            all(board[c, r] == player)
            for r in range(COLUMN_HEIGHT)
            for c in (list(range(n, n + FOUR)) for n in range(NUM_COLUMNS - FOUR + 1))
        )
        or any(
            np.all(board[diag] == player)
            for diag in (
                (range(ro, ro + FOUR), range(co, co + FOUR))
                for ro in range(0, NUM_COLUMNS - FOUR + 1)
                for co in range(0, COLUMN_HEIGHT - FOUR + 1)
            )
        )
        or any(
            np.all(board[diag] == player)
            for diag in (
                (range(ro, ro + FOUR), range(co + FOUR - 1, co - 1, -1))
                for ro in range(0, NUM_COLUMNS - FOUR + 1)
                for co in range(0, COLUMN_HEIGHT - FOUR + 1)
            )
        )
    )


# Montecarlo


def _mc(board, player):
    p = -player
    while valid_moves(board):
        p = -p
        c = np.random.choice(valid_moves(board))
        play(board, c, p)
        if four_in_a_row(board, p):
            return p
    return 0


def montecarlo(board, player):
    montecarlo_samples = 20
    cnt = Counter(_mc(np.copy(board), player) for _ in range(montecarlo_samples))
    return (cnt[1] - cnt[-1]) / montecarlo_samples


def eval_board(board, player):
    if four_in_a_row(board, 1):
        # Alice won
        return 1
    elif four_in_a_row(board, -1):
        # Bob won
        return -1
    else:
        # Not terminal, let's simulate...
        return montecarlo(board, player)


# MCTS


def gen_board():
    return np.zeros((NUM_COLUMNS, COLUMN_HEIGHT), dtype=np.byte)


def ucb(s_p, s, w, c=1):
    return (w / s) + c * math.sqrt(math.log(s_p) / s)


def is_terminal(board):
    if not valid_moves(board):
        return True
    for p in [-1, 1]:
        if four_in_a_row(board, p):
            return True
    return False


class node:
    def __init__(self, parent, board, player):
        self.state = board
        self.player = player
        self.children = set()
        self.parent = parent
        self.simulations = 0
        self.wins = 0

    def select(self):
        best_node = self
        while best_node.children and all(
            child.simulations > 0 for child in best_node.children
        ):
            best_node = max(best_node.children, key=lambda child: child.get_ucb())
        return best_node

    def expand(self):
        if not self.children:
            for c in valid_moves(self.state):
                play(self.state, c, self.player)
                self.children.add(node(self, np.copy(self.state), -self.player))
                take_back(self.state, c)

    def simulate(self):
        winner = _mc(np.copy(self.state), self.player)

        # backpropagation
        node = self
        while node is not None:
            node.simulations += 1
            if winner != node.player:
                node.wins += 1
            node = node.parent

    def get_ucb(self):
        if not self.parent:
            return None
        return ucb(self.parent.simulations, self.simulations, self.wins)


def run_mcts(node):
    node = node.select()  # select node using usb
    if is_terminal(node.state):
        return
    node.expand()
    node = random.choice([child for child in node.children if child.simulations == 0])
    node.simulate()


def get_best(node):
    if not node.children:
        return None
    return max(node.children, key=lambda child: child.wins / child.simulations)


def print_board(board):
    for r in reversed(range(COLUMN_HEIGHT)):
        print("|", end=" ")
        for c in range(NUM_COLUMNS):
            print(SYMBOLS[board[c][r]], end=" ")
        print("|")

    print(" ", end=" ")
    for x in range(NUM_COLUMNS):
        print(x + 1, end=" ")
    print()


def main():
    root = node(None, gen_board(), 1)
    current_node = root

    while valid_moves(current_node.state):
        print_board(current_node.state)
        for _ in range(500):
            run_mcts(current_node)
        for p in [-1, 1]:
            if four_in_a_row(current_node.state, p):
                print(f"Player {SYMBOLS[p]} won")
        current_node = get_best(current_node)
        if current_node is None:
            break
        print()


if __name__ == "__main__":
    main()
