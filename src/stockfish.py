import logging
import os

import chess
import chess.engine

logger = logging.getLogger(__name__)

def getExpectedResult(board):
    logger.info("Calculating expected result")
    with chess.engine.SimpleEngine.popen_uci(os.environ.get("STOCKFISH_PATH")) as engine:
        info = engine.analyse(board, chess.engine.Limit(time=10.0))
        score = info["score"].relative

    if isinstance(score, chess.engine.Mate):
        sign = 1 if score.mate() > 0 else -1
        scoreValue = 10 * sign
    else:
        scoreValue = score.score()

    logger.info(f"The expected result is {scoreValue / 100:.2f}")
    return scoreValue / 100


if __name__ == "__main__":
    fen = "r1bqkbnr/pppppppp/n7/8/8/5N2/PPPPPPPP/RNBQKB1R w KQkq - 0 1"  # Example position
    board = chess.Board(fen)
    print(getExpectedResult(board))