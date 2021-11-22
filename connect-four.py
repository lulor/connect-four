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


# MinMax


# def other(player):
#     return player * -1


def score_is_better(score, current_best, player):
    if player == 1:
        return score > current_best
    else:
        return score < current_best


def update_alpha_beta(alpha, beta, best_score, player):
    if player == 1:
        return max(alpha, best_score), beta
    else:
        return alpha, min(beta, best_score)


def print_board(board):
    symbols = {1: "X", -1: "O", 0: "-"}

    for r in reversed(range(COLUMN_HEIGHT)):
        print("|", end=" ")
        for c in range(NUM_COLUMNS):
            print(symbols[board[c][r]], end=" ")
        print("|")

    print(" ", end=" ")
    for x in range(NUM_COLUMNS):
        print(x, end=" ")
    print()


def eval_for_player(board, player):
    possibilites = np.array(
        [
            np.sum(board[c, r])
            for c in range(NUM_COLUMNS)
            for r in (list(range(n, n + FOUR)) for n in range(COLUMN_HEIGHT - FOUR + 1))
            if -player not in board[c, r]
        ]
        + [
            np.sum(board[c, r])
            for r in range(COLUMN_HEIGHT)
            for c in (list(range(n, n + FOUR)) for n in range(NUM_COLUMNS - FOUR + 1))
            if -player not in board[c, r]
        ]
        + [
            np.sum(board[diag])
            for diag in (
                (range(ro, ro + FOUR), range(co, co + FOUR))
                for ro in range(0, NUM_COLUMNS - FOUR + 1)
                for co in range(0, COLUMN_HEIGHT - FOUR + 1)
            )
            if -player not in board[diag]
        ]
        + [
            np.sum(board[diag])
            for diag in (
                (range(ro, ro + FOUR), range(co + FOUR - 1, co - 1, -1))
                for ro in range(0, NUM_COLUMNS - FOUR + 1)
                for co in range(0, COLUMN_HEIGHT - FOUR + 1)
            )
            if -player not in board[diag]
        ]
    )

    return np.sum(np.where(np.abs(possibilites) == 3, possibilites * 10, possibilites))


def eval(board):
    return eval_for_player(board, 1) + eval_for_player(board, -1)


def check_win(board):
    if four_in_a_row(board, 1):
        return 1
    elif four_in_a_row(board, -1):
        return 2
    else:
        return 0


def minmax(board, depth, alpha, beta, player):
    if four_in_a_row(board, player):
        return None, (player * math.inf)
    elif four_in_a_row(board, -player):
        return None, (-player * math.inf)
    if depth == 0:
        return None, eval(board)
    best_score = -player * math.inf
    best_move = None
    for c in valid_moves(board):
        # if there are valid moves, initialize the best move to the first available
        if best_move is None:
            best_move = c
        play(board, c, player)
        _, score = minmax(board, depth - 1, alpha, beta, -player)
        take_back(board, c)
        if score_is_better(score, best_score, player):
            best_score = score
            best_move = c
        alpha, beta = update_alpha_beta(alpha, beta, best_score, player)
        if alpha >= beta:
            break
    return best_move, best_score


def main():
    player1_is_ai = True
    board = np.zeros((NUM_COLUMNS, COLUMN_HEIGHT), dtype=np.byte)
    # board = np.array(
    #     [
    #         [0, 0, 0, 0, 0, 0],
    #         [-1, 1, -1, 1, -1, -1],
    #         [1, -1, 1, -1, 1, 1],
    #         [1, -1, 1, -1, -1, -1],
    #         [-1, 1, -1, 1, 1, 1],
    #         [1, -1, 1, -1, 1, 0],
    #         [1, -1, 0, 0, 0, 0],
    #     ]
    # )
    player = 1
    alpha = -math.inf
    beta = math.inf

    print_board(board)

    while valid_moves(board):
        print()
        if player1_is_ai or player == -1:
            next_move, score = minmax(board, 5, alpha, beta, player)
        if (not player1_is_ai) and player == 1:
            next_move = int(input("Choose column:"))
        play(board, next_move, player)
        print_board(board)
        winner = check_win(board)
        if winner != 0:
            print(f"Player {winner} won")
            break
        player = -player


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
