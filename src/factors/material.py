import chess
import logging

from src.factors.util import calculateMaterialTotal
from src.params import Params

logger = logging.getLogger(__name__)

def calculatedMaterialImbalance(board, side):
    """
    @brief
    Calculates the material imbalance of the board that is given.

    @details
    It uses the pieceValues defined in globals and calculates the total value of all white and black pieces and then
    subtracts the black piece value from the white one. The result will be positive if white has a higher value than
    black. A negative value means that black has a higher total piece value

    @param board: The board to use for the calculations
    @return: The total value of all white pieces minus the total value of all black pieces
    """
    logger.info("Calculating material imbalance")

    material = calculateMaterialTotal(board)

    logger.info(f"The total material value of white is {material[chess.WHITE]}")
    logger.info(f"The total material value of black is {material[chess.BLACK]}")
    return (material[chess.WHITE] - material[chess.BLACK]) * Params.materialImbalanceMultiplier()