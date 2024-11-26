import chess
import logging
from globals import kingCenterEndgameBonusValue, pawnKingproximityBonusValue, winningExchangeBonusValue, neutralExchangeBonusValue
from src.factors.globals import centerSquares
from src.factors.util import otherSide, calculateMaterialTotal, getGamestatus, Gamestatus

logger = logging.getLogger(__name__)

def endgameConsiderations(board, side):
    """
    Calculates a representational value of the endgame considerations for the given side on the board.

    Calculating the activity score (for the king) and the simplification possibilities.
    :param board: The board to use for the calculations
    :param side: The side with the king to calculate the safety of (chess.WHITE or chess.BLACK)
    :return: Total value of piece activity
    """

    logger.debug("Calculating endgame considerations")

    if getGamestatus(board) == Gamestatus.ENDGAME:
        return 0

    activityScore = 0
    simplificationScore = 0
    if len(list(board.pieces(chess.QUEEN, otherSide(side)))) == 0:
        kingSquare = board.king(side)
        if kingSquare in centerSquares:
            activityScore += kingCenterEndgameBonusValue

        for pawnSquare in board.pieces(chess.PAWN, side):
            if chess.square_distance(kingSquare, pawnSquare) <= 1:
                activityScore += pawnKingproximityBonusValue
    logger.debug(f"The endgame consideration activity score is {activityScore}.")

    # simplification
    for move in board.legal_moves:

        if board.is_capture(side):
            attacker = board.piece_at(move.from_square)
            defender = board.piece_at(move.to_square)

            if attacker and defender:
                attackerValue = attacker.piece_type
                defenderValue = defender.piece_type

                if attackerValue < defenderValue:
                    simplificationScore += winningExchangeBonusValue
                elif attackerValue == defenderValue:
                    simplificationScore += neutralExchangeBonusValue

        board.pop()
    logger.debug(f"The endgame consideration simplification score value is {activityScore}.")

    totalValue = activityScore + simplificationScore
    logger.debug(f"The total endgame consideration score is {totalValue}.")
    return totalValue