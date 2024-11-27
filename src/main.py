import chess, chess.pgn
import chess.engine
import logging
import random
from src.globals import STOCKFISH_PATH, PGN_FILE

logger = logging.getLogger(__name__)

def extractRandomPosition():
    with open(PGN_FILE, "r") as file:
        game_count = 0
        while chess.pgn.read_game(file): # 293000
            game_count += 1
            if game_count % 1000 == 0:
                print(game_count)

        for i, game in enumerate(iter(lambda: chess.pgn.read_game(file), None)):
            if i == game_count:
                return game
        games = []

    randomGame = random.choice(games)
    board = randomGame.board()
    positions = []
    for move in randomGame.mainline_moves():
        board.push(move)
        positions.append(board.fen())

    randomPosition = random.choice(positions)
    return randomPosition


def getExpectedResult(board):
    logger.debug("Calculating expected result")
    with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine:
        info = engine.analyse(board, chess.engine.Limit(time=2.0))
        score = info["score"].relative

    logger.debug(f"The expected result is {score.score() / 100:.2f}")
    return score.score() / 100

if __name__ == "__main__":
    fen = "r1bqkbnr/pppppppp/n7/8/8/5N2/PPPPPPPP/RNBQKB1R w KQkq - 0 1"  # Example position
    board = chess.Board(fen)

    getExpectedResult(extractRandomPosition())