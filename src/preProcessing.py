import random

import chess
import chess.pgn
from globals import PGN_FILE
from src.globals import PGN_PATH


def extractGames(file, gamesPerFile, amountOfFilesToCreate, naming, startValue=0):
    with open(file, "r") as f:
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
            return None #TODO make error. this meant that the start value is larger than the number of games
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
                positions.append(node.board().fen())
            if positions:
                randomFen = random.choice(positions)
                output.write(str(randomFen)+"\n")
            count += 1

extractGames(PGN_FILE, 1024, 5, "training/")
extractGames(PGN_FILE, 1024, 5, "testing/", 1024*5)