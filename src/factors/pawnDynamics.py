import chess
import logging
from src.params import Params

logger = logging.getLogger(__name__)

def pawnDynamics(board, side):
    """
    @brief
    Calculates a representational value for the pawn dynamics for a given side of the board.

    @details
    Calculating the pawn break and pawn structure scores.
    @param board: The board to use for the calculations
    @param side: The side with the king to calculate the safety of (chess.WHITE or chess.BLACK)
    @return: Total value of pawn dynamics
    """
    logger.info("Calculating pawn dynamics")

    pawnBreakScore = 0
    structureScore = 0

    for move in list(board.legal_moves):
        if board.piece_at(move.from_square) and board.piece_at(move.from_square).piece_type == chess.PAWN:
            board.push(move)
            if board.is_capture(move):
                pawnBreakScore += Params.pawnBreakBonusValue
            if board.is_check():
                pawnBreakScore += Params.pawnBreakWithKingExposureBonusValue
            board.pop()

    logger.info(f"The pawn dynamics structure score value is {structureScore}.")

    totalValue = 0
    logger.info(f"The pawn dynamics total value is {totalValue}.")
    return totalValue