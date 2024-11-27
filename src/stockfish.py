import logging
import chess
from globals import STOCKFISH_PATH

logger = logging.getLogger(__name__)

def getExpectedResult(board):
    logger.info("Calculating expected result")
    with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine:
        info = engine.analyse(board, chess.engine.Limit(time=2.0))
        score = info["score"].relative

    logger.info(f"The expected result is {score.score() / 100:.2f}")
    return score.score() / 100


if __name__ == "__main__":
    fen = "r1bqkbnr/pppppppp/n7/8/8/5N2/PPPPPPPP/RNBQKB1R w KQkq - 0 1"  # Example position
    board = chess.Board(fen)
    print(getExpectedResult(board))