class Logger:
    def __init__(self):
        self.buffer = []

    def print(self, *objs):
        for obj in objs:
            self.buffer.append(obj)

    def log_all(self, file=None):
        if file is None:
            for obj in self.buffer:
                print(obj)
        else:
            with open(file, "w") as file:
                for obj in self.buffer:
                    file.write(repr(obj) + "\n")
