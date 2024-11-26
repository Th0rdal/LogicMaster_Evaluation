import chess
import logging
from globals import strongThreatBonusValue, mediumThreatBonusValue, weakThreatBonusValue
logger = logging.getLogger(__name__)

def threats(board, side):
    """
    @brief
    Calculating a representational value of threats for a given side of the board.

    @details
    Calculating the threat score (looking at possible captures of the enemy).

    @param board: The board to use for the calculations
    @param side: The side with the king to calculate the safety of (chess.WHITE or chess.BLACK)
    @return: Total value of threats
    """

    logger.debug("Calculating threats and counter threats")

    threatScore = 0

    for move in board.legal_moves:
        board.push(move)

        attackedSquares = board.attacks(move.to_square)

        for square in attackedSquares:
            piece = board.piece_at(square)
            if piece and piece.color != side:
                if piece.piece_type == chess.KING:
                    threatScore += strongThreatBonusValue
                elif piece.piece_type in [chess.QUEEN, chess.ROOK]:
                    threatScore += mediumThreatBonusValue
                elif piece.piece_type in [chess.BISHOP, chess.KNIGHT]:
                    threatScore += weakThreatBonusValue
        board.pop()

    logger.debug(f"The threats threat score value is {threatScore}.")

    totalValue = threatScore
    logger.debug(f"The total threat score value is {totalValue}.")
    return totalValue