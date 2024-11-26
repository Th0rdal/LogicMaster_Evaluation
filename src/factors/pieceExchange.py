import chess
import logging
from globals import exchangeScoreBonusValue, exchangeScorePenaltyValue, strongCompensationThresholdValue, strongSacrificeBonusValue, mediumCompensationThresholdValue, mediumSacrificeBonusValue
from src.factors.globals import centerSquares
from src.factors.util import otherSide

logger = logging.getLogger(__name__)

def pieceExchange(board, side):
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
                    exchangeScore += exchangeScoreBonusValue
                elif attackerPiece > defenderPiece:
                    exchangeScore += exchangeScorePenaltyValue

                # calculate sacrifice score
                board.push(move)

                centerControl = len(
                    [square for square in centerSquares if board.is_attacked_by(side, square)]
                )
                kingExposure = len(board.attackers(otherSide(side), board.king(otherSide(side))))
                activityBonus = len(list(board.legal_moves))

                compensation = centerControl + kingExposure + activityBonus
                if compensation >= strongCompensationThresholdValue:
                    sacrificeScore += strongSacrificeBonusValue
                elif compensation >= mediumCompensationThresholdValue:
                    sacrificeScore += mediumSacrificeBonusValue

                board.pop()

    logger.debug(f"The piece exchange score value is {exchangeScore}.")
    logger.debug(f"The sacrifice score value is {sacrificeScore}.")

    totalValue = exchangeScore + sacrificeScore
    logger.debug(f"The total piece exchange value is {totalValue}.")
    return totalValue