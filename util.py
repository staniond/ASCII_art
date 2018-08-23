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


class ProgressBar:
    def __init__(self, width, max_value):
        self.width = width*2-1
        self.max_value = max_value

    def get_bar(self, value):
        if value is not None and self.max_value is not None:
            return f"|{' '*(self.width-1)}|\n" \
                   f"|{'>'*int(self.width*(value/self.max_value))}" \
                   f"{'-'*int(self.width*(1-value/self.max_value))}|\n" \
                   f"|{' '*(self.width-1)}|\n"
        else:
            return ""
