import logging
from src.params import Params
from src.globals import CENTER_SQUARE
from src.factors.util import otherSide

logger = logging.getLogger(__name__)

def pieceExchange(board, side):
    """
    @brief
    Calculates a representational value of the piece exchange for the given side of the board.

    @details
    Calculating the piece exchange score and piece sacrifice score.
    @param board: The board to use for the calculations
    @param side: The side with the king to calculate the safety of (chess.WHITE or chess.BLACK)
    @return: Total value of piece exchange
    """
    logger.debug("Calculating piece exchanges")

    exchangeScore = 0
    sacrificeScore = 0

    for move in board.legal_moves:
        if board.is_capture(move):
            attacker = board.piece_at(move.from_square)
            defender = board.piece_at(move.to_square)

            if attacker and defender:
                attackerPiece = attacker.piece_type
                defenderPiece = defender.piece_type

                if attackerPiece < defenderPiece:
                    exchangeScore += Params.exchangeScoreBonusValue()
                elif attackerPiece > defenderPiece:
                    exchangeScore += Params.exchangeScorePenaltyValue()

                # calculate sacrifice score
                board.push(move)

                centerControl = len(
                    [square for square in CENTER_SQUARE if board.is_attacked_by(side, square)]
                )
                kingExposure = len(board.attackers(otherSide(side), board.king(otherSide(side))))
                activityBonus = len(list(board.legal_moves))

                compensation = centerControl + kingExposure + activityBonus
                if compensation >= Params.strongCompensationThresholdValue():
                    sacrificeScore += Params.strongSacrificeBonusValue()
                elif compensation >= Params.mediumCompensationThresholdValue():
                    sacrificeScore += Params.mediumSacrificeBonusValue()

                board.pop()

    logger.debug(f"The piece exchange score value is {exchangeScore}.")
    logger.debug(f"The sacrifice score value is {sacrificeScore}.")

    totalValue = exchangeScore + sacrificeScore
    logger.debug(f"The total piece exchange value is {totalValue}.")
    return totalValue