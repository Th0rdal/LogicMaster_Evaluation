import os
import random

import chess
import chess.pgn
from globals import PGN_FILE, PGN_PATH


def extractGames(file, gamesPerFile, amountOfFilesToCreate, naming, startValue=0):
    with open(os.path.abspath(os.path.join(os.getcwd(), file)), "r") as f:
        filesCreated = 0
        count = 0
        output = None
        game = None
        while count < startValue:
            game = chess.pgn.read_game(f)
            count += 1
            if game is None:
                break
        if game is None and count > 0:
            return ValueError("Start value is out of bounds.")
        count = 0
        if output is None:
            filesCreated += 1
            output = open(PGN_PATH + naming + str(filesCreated), "w")
        while True:
            if count == gamesPerFile:
                output.close()
                filesCreated += 1
                if filesCreated > amountOfFilesToCreate:
                    break
                output = open(PGN_PATH + naming + str(filesCreated), "w")
                count = 0
            game = chess.pgn.read_game(f)
            if game is None:
                break
            node = game
            positions = []
            while not node.is_end():
                node = node.variation(0)
                board = node.board()
                if not board.is_game_over():
                    positions.append(board.fen())
            if positions:
                randomFen = random.choice(positions)
                output.write(str(randomFen)+"\n")
            count += 1

extractGames(PGN_FILE, 1024, 5, "training/")
extractGames(PGN_FILE, 1024, 5, "testing/", 1024*5)