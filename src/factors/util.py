import chess
from enum import Enum

from src.factors.globals import pieceValues, maxMaterialValueEndgame


class Gamestatus(Enum):
    OPENING = 1
    ENDGAME = 3

def otherSide(side):
    if side == chess.WHITE:
        return chess.BLACK
    return chess.WHITE

def getGamestatus(board):
    """
    Calculates in what status the game currently is.

    It only differentiates between Opening and Endgame with Endgame defined as both players having less material than
    defined in globals maxMaterialValueEngame.
    :param board: The board to use for calculations
    :return: Gamestatus enum representing the current game status
    """

    material = calculateMaterialTotal(board)
    if material[chess.WHITE] > maxMaterialValueEndgame or material[chess.BLACK] > maxMaterialValueEndgame:
        return Gamestatus.ENDGAME
    return Gamestatus.OPENING

def calculateMaterialTotal(board):
    """
    Calculates the total value of all pieces combined of both players.

    :param board: The board to use for the calculations
    :return: Dictionary with chess.WHITE and chess.BLACK as keys and the total value as value
    """
    material = {chess.WHITE: 0, chess.BLACK: 0}
    for pieceType in pieceValues:
        material[chess.WHITE] += len(board.pieces(pieceType, chess.WHITE)) * pieceValues[pieceType]
        material[chess.BLACK] += len(board.pieces(pieceType, chess.BLACK)) * pieceValues[pieceType]
    return material