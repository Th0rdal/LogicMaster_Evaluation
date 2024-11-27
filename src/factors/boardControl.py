import chess
import logging
from src.params import openFileBonusValue, semiOpenBonusValue, openDiagonalBonusValue, centralSquareAttackedBonusValue, centerSquares

logger = logging.getLogger(__name__)

def boardControl(board, side):
    """
    @brief
    Calculates a representational value of the board control for the given side on the board.

    @details
    Calculating if a queen or rook was on an open rank, a bishop or queen on an open diagonal and if the central square is attacked

    @param board: The board to use for the calculations
    @param side: The side with the king to calculate the safety of (chess.WHITE or chess.BLACK)
    @return: Total value of board control
    """

    logger.debug("Calculating board control")

    fileScore = 0
    diagonalScore = 0
    centralSquaresAttackedScore = 0

    for squares in board.pieces(chess.ROOK, side) | board.pieces(chess.QUEEN, side):
        file = chess.square_file(squares)
        whitePawns = board.pieces(chess.PAWN, chess.WHITE) & chess.BB_FILES[file]
        blackPawns = board.pieces(chess.PAWN, chess.BLACK) & chess.BB_FILES[file]

        if not whitePawns and not blackPawns:
            fileScore += openFileBonusValue
        elif not whitePawns:
            fileScore += semiOpenBonusValue
    logger.debug(f"The board control file score value is {fileScore}.")

    for pieceSquares in board.pieces(chess.BISHOP, side) | board.pieces(chess.QUEEN, side):
        isOpen = True
        for square in board.attacks(pieceSquares):
            if board.piece_at(square) and board.piece_at(square).piece_type == chess.PAWN:
                isOpen = False
                break
        if isOpen:
            diagonalScore += openDiagonalBonusValue
    logger.debug(f"The board control diagonal score value is {diagonalScore}.")

    for square in centerSquares:
        if board.is_attacked_by(side, square):
            centralSquaresAttackedScore += centralSquareAttackedBonusValue
    logger.debug(f"The board control central control score value is {centralSquaresAttackedScore}.")

    totalValue = fileScore + diagonalScore + centralSquaresAttackedScore
    logger.debug(f"The board control total value is {totalValue}.")
    return totalValue