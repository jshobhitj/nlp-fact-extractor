import pickle


class ProcessedTuples:

    def __init__(self, config):
        self.file_path = config.processed_tuples_file
        self.file = open(self.file_path, 'r')

    def __iter__(self):
        return self

    def next(self):
        try:
            return pickle.load(self.file)
        except EOFError:
            self.file.close()
            raise StopIteration
