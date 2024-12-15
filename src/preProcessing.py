import multiprocessing
import os
import random
import time

import chess
import chess.pgn
from globals import PGN_FILE, STOP_ITERATING_SIGN
from src.stockfish import getExpectedResult

def afterProcessFile(fenList, counter):
    global trainingFilesCreated, testingFilesCreated, processes

    while len(processes) >= maxProcesses:
        for process in processes[:]:  # Iterate over a copy of the list
            if not process.is_alive():  # Check if the process has finished
                process.join()  # Ensure the process has completely terminated
                processes.remove(process)  # Remove the completed process
        time.sleep(0.1)  # Add a small delay to prevent busy-waiting

    if counter % 2 == 1:
        trainingFilesCreated += 1
        path = f"training/{trainingFilesCreated}"
    else:
        testingFilesCreated += 1
        path = f"testing/{testingFilesCreated}"
    process = multiprocessing.Process(target=addExpectedValue, args=(fenList, path))
    processes.append(process)
    process.start()

def calculatedExpectedValue(fens):
    return [fen + ":" + str(getExpectedResult(chess.Board(fen))) + "\n" for fen in fens]

def addExpectedValue(lines, path):
    n = 4
    chunk_size = len(lines) // n
    chunks = [lines[i * chunk_size : (i + 1) * chunk_size] for i in range(n - 1)] + [lines[(n - 1) * chunk_size:]]

    with multiprocessing.Pool(processes=4) as pool:
        modifiedLines = pool.map(calculatedExpectedValue, chunks)

    flattenedLines = [item for sublist in modifiedLines for item in sublist]
    with open(os.getenv("BASE_PATH") + "temp", "w") as file:
        for line in flattenedLines:
            file.write(line)
    os.rename(os.getenv("BASE_PATH") + "temp", os.getenv("BASE_PATH") + path)

def extractGames(file, gamesPerFile, amountOfFilesToCreate, filesAlreadyCreated=0, startValue=0):
    with open(os.path.abspath(os.path.join(os.getenv("BASE_PATH"), file)), "r") as f:
        filesCreated = filesAlreadyCreated
        count = 0
        output = []
        game = None
        while count < startValue:
            game = chess.pgn.read_game(f)
            count += 1
            if game is None:
                break
        if game is None and count > 0:
            return ValueError("Start value is out of bounds.")
        count = 0

        while True:
            if count == gamesPerFile:
                filesCreated += 1
                if amountOfFilesToCreate != 0 and filesCreated > amountOfFilesToCreate:
                    break
                afterProcessFile(output, filesCreated)
                output = []
                count = 0
            game = chess.pgn.read_game(f)
            if game is None:
                #TODO remove last output file since it isn't filled correctly
                return amountOfFilesToCreate - filesCreated
            node = game
            positions = []
            while not node.is_end():
                node = node.variation(0)
                board = node.board()
                if not board.is_game_over():
                    positions.append(board.fen())
            if positions:
                randomFen = random.choice(positions)
                output.append(str(randomFen))
            count += 1

    return 0

if __name__ == "__main__":

    numProcesses = 2
    testFilesNeeded = 5
    trainingFilesNeeded = 5
    processes = []
    maxProcesses = 4
    trainingFilesCreated = 0
    testingFilesCreated = 0
    folders = ["training/", "testing/"]
    basePath = os.getenv("BASE_PATH")

    for folder in folders:
        if not os.path.exists(basePath + folder):
            os.mkdir(basePath + folder)

    entries = os.listdir(os.path.abspath(os.path.join(os.getenv("BASE_PATH"), folders[0])))
    largestNumber = 0
    if entries:
        for entry in entries:
            try:
                number = int(entry)
                if largestNumber < number:
                    largestNumber = number
            except ValueError:
                continue

    filesLeft = extractGames(PGN_FILE, 10, testFilesNeeded + trainingFilesNeeded + largestNumber, largestNumber)

    while len(processes) > 0:
        for process in processes[:]:  # Iterate over a copy of the list
            if not process.is_alive():  # Check if the process has finished
                process.join()  # Ensure the process has completely terminated
                processes.remove(process)  # Remove the completed process

    with open(os.getenv("BASE_PATH") + f"testing/{testingFilesCreated}", "a") as file:
        file.write(STOP_ITERATING_SIGN)

    if filesLeft > 0: # replace with getting a new file
        raise Exception("There are " + str(filesLeft) + " files left.")