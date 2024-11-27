import chess
import logging
from src.params import spaceAdvantageMultiplierBonusValue, zugzwangBonusValue

logger = logging.getLogger(__name__)

def spaceAndControl(board, side):
    """
    @brief
    Calculates a representing value for the space and control the chosen side currently has on the board.

    @details
    It adds points for space advantage and for zugzwang.
    @param board: The board to use for the calculations
    @param side: The side with the king to calculate the safety of (chess.WHITE or chess.BLACK)
    @return: Total value of space and control
    """

    logger.debug("Calculating space and control")

    zugzwang = 0

    whiteControl = set()
    blackControl = set()

    for square in chess.SQUARES:
        if board.is_attacked_by(chess.WHITE, square):
            whiteControl.add(square)
        if board.is_attacked_by(chess.BLACK, square):
            blackControl.add(square)

    spaceAdvantage = len(whiteControl) - len(blackControl) if side == chess.WHITE else len(blackControl) - len(whiteControl)
    spaceScore = spaceAdvantage * spaceAdvantageMultiplierBonusValue
    logger.debug(f"The space and control space score value is {spaceScore}.")

    opponentMoves = list(board.legal_moves)
    worstOutcomes = 0

    for move in opponentMoves:
        board.push(move)
        if not any (board.legal_moves): # stalemate check
            worstOutcomes += 1
        board.pop()
    if worstOutcomes == len(opponentMoves):
        zugzwang += zugzwangBonusValue
    logger.debug(f"The space and control zugzwang value is {zugzwang}.")

    totalValue = spaceScore + zugzwang
    logger.debug(f"The space and control total value is {totalValue}.")
    return totalValue