import chess
import logging
from globals import pawnBreakBonusValue, pawnBreakWithKingExposureBonusValue, structureBonusValue
from src.factors.util import otherSide

logger = logging.getLogger(__name__)

def pawnDynamics(board, side):
    logger.debug("Calculating pawn dynamics")

    pawnBreakScore = 0
    structureScore = 0

    for move in list(board.legal_moves):
        if board.piece_at(move.from_square) and board.piece_at(move.from_square).piece_type == chess.PAWN:
            board.push(move)
            if board.is_capture(move):
                pawnBreakScore += pawnBreakBonusValue
            if board.is_check():
                pawnBreakScore += pawnBreakWithKingExposureBonusValue
            board.pop()

    logger.debug(f"The pawn dynamics structure score value is {structureScore}.")

    totalValue = 0
    logger.debug(f"The pawn dynamics total value is {totalValue}.")
    return totalValue