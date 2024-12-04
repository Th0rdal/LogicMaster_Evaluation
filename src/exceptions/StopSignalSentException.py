
class StopSignalSentException(StopIteration):
    def __init__(self, *args):
        super().__init__(*args)