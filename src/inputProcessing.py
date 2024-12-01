from src.main import currentTime


class InputProcessor:

    basePath = "../../resources/" #"/app/resources/"
    currentFile = ""
    index = 1
    currentPath = ""

    def getInputBoard(self):
        """
        This returns the next board input in fen notation. If all boards are processed, it returns None.
        IMPORTANT: Before loading the next file with positions, this function MUST return None, which means that it is finished with the previous file.
        Otherwise, the new file will not be loaded.
        :return: board position in fen notation or None (if done with file)
        """

        with open(self.currentPath) as file:
            for line in file:
                yield line.strip()
        return None

    def loadNextSet(self, boardType):
        """
        creates the path to the next file to get board positions from. It will increment the index after every test.
        It is expected to go in the order training, testing, training, testing, ...
        :param boardType: training or testing, depending on what is wanted
        :return: None
        """
        self.currentPath = self.basePath + boardType + "/" + str(self.index)
        if boardType == "testing":
            self.index += 1