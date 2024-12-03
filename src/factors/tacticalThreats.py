import chess
import logging
from src.params import Params
from src.factors.util import otherSide

logger = logging.getLogger(__name__)

def tacticalThreats(board, side):
    """
    @brief
    Calculates a representational value of tactical threats the given side has on the board.

    @details
    Calculates fork score, pin score and skewer score for the side given as parameter
    @param board: The board to use for the calculations
    @param side: The side with the king to calculate the safety of (chess.WHITE or chess.BLACK)
    @return: Total value of tactical threats
    """

    logger.debug("Calculating tactical threats")

    # fork
    forkScore = 0
    for move in board.legal_moves:
        attackedSquare = board.attacks(move.to_square)
        attackedPieces = [board.piece_at(square) for square in attackedSquare if board.piece_at(square)]

        valuablePieces = [p for p in attackedPieces if p.piece_type in [chess.ROOK, chess.QUEEN, chess.KING]]
        if len(valuablePieces) > 1:
            forkScore += Params.forkBonusValue()
    logger.debug(f"The tactical threats fork score value is {forkScore}.")

    # pins
    pinScore = 0
    for attackerSquare in board.pieces(chess.BISHOP, side) | board.pieces(chess.ROOK, side) | board.pieces(chess.QUEEN, side):
        for targetSquare in board.attacks(attackerSquare):
            if board.piece_at(targetSquare) and board.piece_at(targetSquare).color == otherSide(side):
                pinnedPiece = board.piece_at(targetSquare)
                if pinnedPiece.piece_type != chess.KING:
                    for behindSquare in board.attacks(targetSquare):
                        if board.piece_at(behindSquare) and board.piece_at(behindSquare).color == otherSide(side):
                            pinScore += Params.pinBonusValue()
    logger.debug(f"The tactical threats pin score value is {pinScore}.")

    # skewers
    skewerScore = 0
    for attackerSquare in board.pieces(chess.QUEEN, side) | board.pieces(chess.ROOK, side):
        for targetSquare in board.attacks(attackerSquare):
            if board.piece_at(targetSquare) and board.piece_at(targetSquare).piece_type == chess.KING:
                for behindSquare in board.attacks(targetSquare):
                    if board.piece_at(behindSquare) and board.piece_at(behindSquare).color == otherSide(side):
                        skewerScore += Params.skewerBonusValue()
    logger.debug(f"The tactical threats skewer score value is {skewerScore}.")

    totalValue = forkScore + pinScore + skewerScore
    logger.debug(f"The total tactical threats value is {totalValue}")
    return totalValue