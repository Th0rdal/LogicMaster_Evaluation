import chess

CENTER_SQUARE = {chess.E4, chess.D4, chess.E5, chess.D5}

# util
PIECE_VALUE = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 5,
}

STOCKFISH_PATH = "stockfish17/stockfish/stockfish-windows-x86-64-avx2.exe"
PGN_FILE = "../resources/lichess_db_standard_rated_2013-07.pgn"
PGN_PATH = "../resources/"