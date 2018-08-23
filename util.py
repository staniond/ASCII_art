import subprocess as sp


def get_terminal_size():
    size = sp.run(["stty", "size"], stdout=sp.PIPE).stdout.decode()[:-1].split(" ")
    return int(size[1]), int(size[0])


class Logger:
    def __init__(self, log, path):
        self.log = log
        self.path = path
        self.buffer = []

    def print(self, *objs):
        if self.log:
            for obj in objs:
                self.buffer.append(obj)

    def log_all(self, to_file=False):
        if self.log:
            if not to_file:
                for obj in self.buffer:
                    print(obj)
            else:
                with open(self.path, "w") as file:
                    for obj in self.buffer:
                        file.write(str(obj) + "\n")


class ProgressBar:
    def __init__(self, width, frames):
        self.frames = frames
        self.width = width * 2 - 1

    def get_bar(self, frame_count):
        return f"|{' '*(self.width-1)}|\n" \
               f"|{'>'*int(self.width*(frame_count/self.frames))}" \
               f"{'-'*int(self.width*(1-frame_count/self.frames))}|\n" \
               f"|{' '*(self.width-1)}|\n"


if __name__ == '__main__':
    print(get_terminal_size())
