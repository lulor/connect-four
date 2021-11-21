from collections import Counter
import numpy as np
import math

NUM_COLUMNS = 7
COLUMN_HEIGHT = 6
FOUR = 4


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


# MinMax


def other(player):
    return player * -1


def score_is_better(score, current_best, player):
    if player == 1:
        return score > current_best
    else:
        return score < current_best


def prune(alpha, beta, score, player):
    if player == 1:
        return score >= beta
    else:
        return score <= alpha


def update_alpha_beta(alpha, beta, best_score, player):
    if player == 1:
        return max(alpha, best_score), beta
    else:
        return alpha, min(beta, best_score)


def print_board(board):
    for c in range(NUM_COLUMNS):
        column = np.array([2 if x == -1 else x for x in board[c, :]])
        print(f"{c} {column}")


def best_evaluation(evaluations, player):
    if player == 1:
        return max(evaluations, key=lambda k: k[1])
    return min(evaluations, key=lambda k: k[1])


def check_win(board):
    won = True
    if four_in_a_row(board, 1):
        print(f"Player 1 won")
    elif four_in_a_row(board, -1):
        print(f"Player 2 won")
    else:
        won = False
    return won


def minmax(board, player, alpha, beta, depth):
    evaluations = []
    if depth == 0:
        return None, eval_board(board, player)
    possible_moves = valid_moves(board)
    for c in possible_moves:
        _, val = minmax(board, -player, alpha, beta, depth - 1)
        evaluations.append((c, val))
    return best_evaluation(evaluations, player)


def main():
    player1_is_ai = True
    board = np.zeros((NUM_COLUMNS, COLUMN_HEIGHT), dtype=np.byte)
    player = 1
    alpha = -math.inf
    beta = math.inf

    print_board(board)

    while valid_moves(board):
        print()
        if player1_is_ai or player == -1:
            next_move, score = minmax(board, player, alpha, beta, 3)
        if (not player1_is_ai) and player == 1:
            next_move = int(input("Choose column:"))
        play(board, next_move, player)
        print_board(board)
        if check_win(board):
            break
        player = other(player)


def dbg():
    board = np.zeros((NUM_COLUMNS, COLUMN_HEIGHT), dtype=np.byte)
    play(board, 0, -1)
    play(board, 0, -1)
    play(board, 0, -1)
    play(board, 1, -1)
    play(board, 1, -1)

    play(board, 3, 1)
    play(board, 3, 1)
    play(board, 3, 1)
    play(board, 3, 1)
    play(board, 4, 1)
    play(board, 4, 1)
    play(board, 5, 1)

    diags = [
        board[diag]
        for diag in (
            (range(ro, ro + FOUR), range(co + FOUR - 1, co - 1, -1))
            for ro in range(0, NUM_COLUMNS - FOUR + 1)
            for co in range(0, COLUMN_HEIGHT - FOUR + 1)
        )
        if -1 not in board[diag]
    ]

    print(board)

    for diag in diags:
        print(f"{diag} score = {sum(diag) ** 4}")


if __name__ == "__main__":
    main()
