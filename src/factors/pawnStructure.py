import chess
import logging
from globals import isolatedPawnPenaltyValue, doublePawnPenaltyValue, backwardPawnPenaltyValue, passedPawnBonusValue, advancedPassedPawnBonusValue, chainLengthMultiplierBonusValue
from src.factors.util import otherSide

logger = logging.getLogger(__name__)

def pawnStructure(board, side):
    """
    Calculates a representing value for the pawn structure

    Calculates isolated pawn, double pawn and backward pawn penalty as well as passed pawn and pawn chain boni.
    :param board: The board to use for the calculations
    :param side: The side with the king to calculate the safety of (chess.WHITE or chess.BLACK)
    :return: Total value of pawn structure
    """

    logger.debug("Calculating pawn structure")

    # isolated pawns
    isolatedPenalty = 0
    for pawnSquare in board.pieces(chess.PAWN, side):
        file = chess.square_file(pawnSquare)
        # Check if adjacent files are empty of friendly pawns
        if not any(board.pieces(chess.PAWN, side) & chess.BB_FILES[file + offset] for offset in [-1, 1] if 0 <= file + offset <= 7):
            isolatedPenalty -= isolatedPawnPenaltyValue
    logger.debug(f"The pawn structure isolated penalty is {isolatedPenalty}.")

    # double pawns
    doubledPawnPenalty = 0
    for file in range(8):
        pawnsOnFile = sum(1 for square in chess.BB_FILES[file] if board.piece_at(square) == chess.Piece(chess.PAWN, side))
        if pawnsOnFile > 1:
            doubledPawnPenalty += doublePawnPenaltyValue
    logger.debug(f"The pawn structure double pawn penalty is {doubledPawnPenalty}.")

    # backwards pawns
    backwardPawnPenalty = 0
    for pawnSquare in board.pieces(chess.PAWN, side):
        file = chess.square_file(pawnSquare)
        if not any (board.pieces(chess.PAWN, side) & chess.BB_FILES[file + offset] for offset in [-1, 1] if 0 <= file + offset <= 7):
            if board.piece_at(chess.square(file, chess.square_rank(pawnSquare) + 1)) is not None:
                backwardPawnPenalty += backwardPawnPenaltyValue
    logger.debug(f"The pawn structure backwards pawn penalty is {backwardPawnPenalty}.")

    # passed pawn
    passedPawnBonus = 0
    for pawnSquare in board.pieces(chess.PAWN, side):
        file = chess.square_file(pawnSquare)
        rank = chess.square_rank(pawnSquare)
        # Check no opposing pawns block on the file or adjacent files
        if not any(board.pieces(chess.PAWN, otherSide(side)) & chess.BB_FILES[file + offset] for offset in [-1, 0, 1] if 0 <= file + offset <= 7):
            passedPawnBonus += passedPawnBonusValue
            if rank >= 4:  # Advanced pawn
                passedPawnBonus += advancedPassedPawnBonusValue
    logger.debug(f"The pawn structure passed pawn bonus is {passedPawnBonus}.")

    # pawn chains
    chainBonus = 0
    visited = set()  # To avoid double-counting chains
    for pawnSquare in board.pieces(chess.PAWN, side):
        if pawnSquare in visited:
            continue
        chainLength = 1
        currentSquare = pawnSquare
        # Trace the chain
        while True:
            nextSquare = chess.square(chess.square_file(currentSquare) + (1 if side == chess.WHITE else -1), chess.square_rank(currentSquare) + (1 if side == chess.WHITE else -1))
            if board.piece_at(nextSquare) == chess.Piece(chess.PAWN, side):
                chainLength += 1
                visited.add(nextSquare)
                currentSquare = nextSquare
            else:
                break
        chainBonus += chainLength * chainLengthMultiplierBonusValue
    logger.debug(f"The pawn structure chain bonus is {chainBonus}.")

    totalValue = (passedPawnBonus + chainBonus) - (isolatedPenalty + doubledPawnPenalty + backwardPawnPenalty)
    logger.debug(f"The total pawn structure value is {totalValue}.")
    return totalValue
