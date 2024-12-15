import logging
import chess

from src.factors.boardControl import boardControl
from src.factors.endgameConsiderations import endgameConsiderations
from src.factors.kingSafety import kingSafety
from src.factors.material import calculatedMaterialImbalance
from src.factors.pawnDynamics import pawnDynamics
from src.factors.pawnStructure import pawnStructure
from src.factors.pieceActivity import pieceActivity
from src.factors.pieceExchange import pieceExchange
from src.factors.spaceAndControl import spaceAndControl
from src.factors.specialCases import specialCases
from src.factors.tacticalThreats import tacticalThreats
from src.factors.threatsandCounterThreats import threats
from src.globals import minimalValue, maximalValue

logger = logging.getLogger(__name__)

def positionCalculator(board):
    logger.debug("Calculating actual position!")
    total = [0, 0]  #white is index 0, black is index 1

    for index, side in enumerate([chess.WHITE, chess.BLACK]):
        total[index] = (boardControl(board, side) +
                 endgameConsiderations(board, side) +
                 kingSafety(board, side) +
                 calculatedMaterialImbalance(board, side) +
                 pawnDynamics(board, side) +
                 pawnStructure(board, side) +
                 pieceActivity(board, side) +
                 pieceExchange(board, side) +
                 spaceAndControl(board, side) +
                 specialCases(board, side) +
                 tacticalThreats(board, side) +
                 threats(board, side))

    # if white has a higher score, actual is positive and white has an advantage
    actual = total[0] - total[1]

    if actual < minimalValue:
        return minimalValue
    if actual > maximalValue:
        return maximalValue
    return actual

