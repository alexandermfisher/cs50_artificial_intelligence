"""
Tic Tac Toe Player
"""

import math
from copy import deepcopy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """

    ### Counts the amount of turns each player has taken.
    X_count = 0
    O_count = 0
    for i in board:
        for j in i:
            if j == "X":
                X_count += 1
            elif j == "O":
                O_count += 1

    if terminal(board):
        return None
    elif X_count == O_count:
        return "X"
    else:
        return "O"


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possible_moves = set()
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                possible_moves.add((i,j))

    return possible_moves


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    updated_board = deepcopy(board)
    try:
        if action not in actions(board):
            raise ValueError
        else:
            updated_board[action[0]][action[1]] = player(board)

    except ValueError:
        print("Invalid action. Only EMPTY spaces are valid places to make a move")

    return updated_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """

    ### check for horizontal wins
    for row in board:
        if all(col == row[0] for col in row): return row[0]
    ### check for vertical and diagonal wins
    if board[0][0] == board[1][0] == board[2][0]: return board[0][0]
    elif board[0][1] == board[1][1] == board[2][1]: return board[0][1]
    elif board[0][2] == board[1][2] == board[2][2]: return board[0][2]
    elif board[0][0] == board[1][1] == board[2][2]: return board[0][0]
    elif board[0][2] == board[1][1] == board[2][0]: return board[0][2]
    else: return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    ### check to see if there is a winner
    if winner(board) != None:   return True

    ### check to see if board is full
    for i in board:
        for j in i:
            if j == EMPTY:
                return False

    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    who_won = winner(board)
    if who_won == "X": return 1
    elif who_won == "O": return -1
    else: return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if board == initial_state():
        return (0,0)

    if player(board) == "X":
        v = -math.inf
        move = None
        for action in actions(board):
            min_val = min_value(result(board, action))
            if min_val > v:
                v = min_val
                move = action
    else:
        v = math.inf
        move = None
        for action in actions(board):
            max_val = max_value(result(board, action))
            if max_val < v:
                v = max_val
                move = action

    return move


def max_value(board):
    if terminal(board):
        return utility(board)
    v = -math.inf
    for action in actions(board):
        v = max(v,min_value(result(board,action)))
    return v


def min_value(board):
    if terminal(board):
        return utility(board)
    v = math.inf
    for action in actions(board):
        v = min(v,max_value(result(board,action)))
    return v
