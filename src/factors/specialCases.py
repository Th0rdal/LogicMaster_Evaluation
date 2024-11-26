import chess
import logging
from globals import backRankBonusValue, backRankPenaltyValue, promotionScoreBonusValue, promotionPossibilityBonusValue
from src.factors.util import otherSide

logger = logging.getLogger(__name__)

def specialCases(board, side):
    """
    @brief
    Calculates a representational value of the special cases for the given side of the board.

    @details
    Currently, no special cases are defined. Might not come!
    @param board:
    @param side:
    @return:
    """
    return 0