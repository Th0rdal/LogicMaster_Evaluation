import chess
import logging
from src.params import Params
from src.globals import CENTER_SQUARE

logger = logging.getLogger(__name__)

def pieceActivity(board, side):
    """
    @brief
    Calculates a representational value of the piece activity for the given side on the board.

    @details
    Calculating the mobility score (total legal moves possible), coordination score (pieces protecting other pieces) and centralization
    (pieces on the files E4, D4, E5, D5).
    @param board: The board to use for the calculations
    @param side: The side with the king to calculate the safety of (chess.WHITE or chess.BLACK)
    @return: Total value of piece activity
    """

    logger.debug("Calculating piece activity")

    mobilityScore = 0
    coordinationScore = 0
    centralizationScore = 0

    # mobility score
    legalMoves = len(list(board.legal_moves))
    mobilityScore += legalMoves * Params.mobilityWeightMultiplierBonusValue()

    for pieceType in chess.PIECE_TYPES:
        for square in board.pieces(pieceType, side):

            # piece coordination
            for attackSquare in board.attacks(square):
                if board.piece_at(attackSquare) and board.piece_at(attackSquare).color == side:
                    coordinationScore += Params.pieceCoordinationBonusValue()
    logger.debug(f"The piece activity mobility score value is {mobilityScore}.")
    logger.debug(f"The piece activity coordination score value is {coordinationScore}.")

    # centralization
    for square in CENTER_SQUARE:
        piece = board.piece_at(square)
        if piece and piece.color == side:
            centralizationScore += Params.centralizationBonusValue()
    logger.debug(f"The piece activity centralization score value is {centralizationScore}.")

    totalValue = mobilityScore + coordinationScore + centralizationScore
    logger.debug(f"The total piece activity value is {totalValue}.")
    return totalValue