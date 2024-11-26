import chess
from globals import pawnShieldBonusValue, exposedKingPenaltyValue, castledBonusValue, notCastledPenaltyValue
from src.factors.util import getGamestatus, Gamestatus
from util import otherSide
import logging

logger = logging.getLogger(__name__)

def kingSafety(board, side):
    """
    Calculates a representing value for the safety the king currently has on the field.

    It adds points for a pawn shield (pawns in front of the king), if the king or spaces in front of him are attacked and how often
    and if the king has been castled.
    :param board: The board to use for the calculations
    :param side: The side with the king to calculate the safety of (chess.WHITE or chess.BLACK)
    :return: Total value of king safety
    """

    logger.debug("Calculating king safety")

    kingSquare = board.king(side)
    kingFile = chess.square_file(kingSquare)
    pawnShield = 0
    exposedPenaltyTotal = 0

    logger.debug(f"The king safety side chosen was {side}")

    for offset in [-1, 0, 1]:
        if 0 <= kingFile + offset <= 7:
            pawnSquare = chess.square(kingFile + offset, chess.square_rank(kingSquare) + (-1 if side == chess.WHITE else 1))
            if board.piece_at(pawnSquare) == chess.Piece(chess.PAWN, side):
                pawnShield += pawnShieldBonusValue
            for attackSquare in board.attacks(pawnSquare):
                if board.piece_at(attackSquare) == chess.Piece(chess.PAWN, otherSide(side)):
                    exposedPenaltyTotal += exposedKingPenaltyValue
    pawnShield = pawnShield if getGamestatus(board) != Gamestatus.ENDGAME else 0
    logger.debug(f"The king safety pawn shield value is {pawnShield}.")

    for attackSquare in board.attacks(kingSquare):
        if board.piece_at(attackSquare) == chess.Piece(chess.PAWN, otherSide(side)):
            exposedPenaltyTotal += exposedKingPenaltyValue

    logger.debug(f"The king safety exposed penalty total is {exposedPenaltyTotal}.")

    castlingBonus = notCastledPenaltyValue if board.has_castling_rights(side) else castledBonusValue
    castlingBonus = castlingBonus if getGamestatus(board) != Gamestatus.ENDGAME else 0
    logger.debug(f"The king safety castling bonus is {castlingBonus}.")

    totalValue = pawnShield - exposedPenaltyTotal + castlingBonus
    logger.debug(f"The king safety total value is {totalValue}.")

    return totalValue