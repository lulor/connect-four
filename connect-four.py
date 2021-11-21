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
    # print(f"play() column, player: {column}, {player}")
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


def count_streaks(board, player, length):
    """Checks how many length-piece lines the player has"""
    return (
        sum(
            all(board[c, r] == player)
            for c in range(NUM_COLUMNS)
            for r in (
                list(range(n, n + length)) for n in range(COLUMN_HEIGHT - length + 1)
            )
        )
        + sum(
            all(board[c, r] == player)
            for r in range(COLUMN_HEIGHT)
            for c in (
                list(range(n, n + length)) for n in range(NUM_COLUMNS - length + 1)
            )
        )
        + sum(
            np.all(board[diag] == player)
            for diag in (
                (range(ro, ro + length), range(co, co + length))
                for ro in range(0, NUM_COLUMNS - length + 1)
                for co in range(0, COLUMN_HEIGHT - length + 1)
            )
        )
        + sum(
            np.all(board[diag] == player)
            for diag in (
                (range(ro, ro + length), range(co + length - 1, co - 1, -1))
                for ro in range(0, NUM_COLUMNS - length + 1)
                for co in range(0, COLUMN_HEIGHT - length + 1)
            )
        )
    )


def eval(board):
    score = 0

    pos_3_streaks = count_streaks(board, 1, 3)
    neg_3_streaks = count_streaks(board, -1, 3)
    pos_2_streaks = count_streaks(board, 1, 2) - pos_3_streaks
    neg_2_streaks = count_streaks(board, -1, 2) - neg_3_streaks

    score += 10 *pos_3_streaks
    score -= 7 *neg_3_streaks
    score += 5 *pos_2_streaks
    score -= 4 *neg_2_streaks

    return score


def check_win(board):
    if four_in_a_row(board, 1):
        print(f"Player 1 won")
    elif four_in_a_row(board, -1):
        print(f"Player -1 won")


def minmax(board, depth, alpha, beta, player):
    if four_in_a_row(board, player):
        return None, (player * math.inf)
    elif four_in_a_row(board, other(player)):
        return None, (other(player) * math.inf)
    if depth == 0:
        return None, eval(board)
    best_score = other(player) * math.inf
    best_move = None
    for c in valid_moves(board):
        play(board, c, player)
        score = minmax(board, depth - 1, alpha, beta, other(player))[1]
        take_back(board, c)
        if score_is_better(score, best_score, player):
            best_score = score
            best_move = c
        if prune(alpha, beta, best_score, player):
            break
        alpha, beta = update_alpha_beta(alpha, beta, best_score, player)
    if best_move is None:
        best_move = c
    return best_move, best_score


def main():
    board = np.zeros((NUM_COLUMNS, COLUMN_HEIGHT), dtype=np.byte)
    player = 1
    alpha = -math.inf
    beta = math.inf

    while valid_moves(board):
        next_move, score = minmax(board, 5, alpha, beta, player)
        if next_move is None:
            break
        play(board, next_move, player)
        print(board)
        print()
        player = other(player)

    check_win(board)


if __name__ == "__main__":
    main()
