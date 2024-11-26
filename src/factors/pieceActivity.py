import chess
import logging
from globals import centerSquares, mobilityWeightMultiplierBonusValue, pieceCoordinationBonusValue, centralizationBonusValue

logger = logging.getLogger(__name__)

def pieceActivity(board, side):
    """
    Calculates a representational value of the piece activity for the given side on the board.

    Calculating the mobility score (total legal moves possible), coordination score (pieces protecting other pieces) and centralization
    (pieces on the files E4, D4, E5, D5).
    :param board: The board to use for the calculations
    :param side: The side with the king to calculate the safety of (chess.WHITE or chess.BLACK)
    :return: Total value of piece activity
    """

    logger.debug("Calculating piece activity")

    mobilityScore = 0
    coordinationScore = 0
    centralizationScore = 0

    for square in board.pieces(chess.PIECE_TYPES, side):

        # mobility score
        legalMoves = len(list(board.legal_moves.from_square(square)))
        mobilityScore += legalMoves * mobilityWeightMultiplierBonusValue

        # piece coordination
        for attackSquare in board.attacks(square):
            if board.piece_at(attackSquare) and board.piece_at(attackSquare).color == side:
                coordinationScore += pieceCoordinationBonusValue
    logger.debug(f"The piece activity mobility score value is {mobilityScore}.")
    logger.debug(f"The piece activity coordination score value is {coordinationScore}.")

    # centralization
    for square in centerSquares:
        piece = board.piece_at(square)
        if piece and piece.color == side:
            centralizationScore += centralizationBonusValue
    logger.debug(f"The piece activity centralization score value is {centralizationScore}.")

    totalValue = mobilityScore + coordinationScore + centralizationScore
    logger.debug(f"The total piece activity value is {totalValue}.")
    return totalValue