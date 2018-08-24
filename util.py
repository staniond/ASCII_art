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
    def __init__(self, video):
        self.frames = video.frames
        self.width = video.res[0] * 2 - 1
        self.duration = video.duration

    def get_bar(self, frame_count, start_time):
        # TODO add time stamp to the middle of the third row
        if self.duration and self.frames:
            return f"|{' '*(self.width-1)}|\n" \
                   f"|{'>'*int(self.width*(frame_count/self.frames))}" \
                   f"{'-'*int(self.width*(1-frame_count/self.frames))}|\n" \
                   f"|{' '*(self.width-1)}|\n"
        elif self.frames:
            return f"|{' '*(self.width-1)}|\n" \
                   f"|{'>'*int(self.width*(frame_count/self.frames))}" \
                   f"{'-'*int(self.width*(1-frame_count/self.frames))}|\n" \
                   f"|{'t'*(self.width-1)}|\n"
        else:
            return ""


if __name__ == '__main__':
    print(get_terminal_size())
