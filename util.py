import os


def get_terminal_size():
    try:
        size = os.get_terminal_size()
        return size[0], size[1]
    except OSError:
        return None


def to_hours_minutes_seconds(seconds):
    return f"{seconds//3600}:{str((seconds%3600)//60).zfill(2)}:{str(seconds%60).zfill(2)}"


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
        self.width = video.res[0] * 2 - 2
        self.duration = round(video.duration)

    def get_bar(self, frame_count):
        if self.duration and self.frames:
            time_info = f"{to_hours_minutes_seconds(int(self.duration*(frame_count/self.frames)))}/" \
                        f"{to_hours_minutes_seconds(self.duration)}"
            left = self.width//2 - len(time_info)//2
            right = self.width - left - len(time_info)
            return f"|{' '*self.width}|\n" \
                   f"|{'>'*round(self.width*(frame_count/self.frames))}" \
                   f"{'-'*round(self.width*(1-frame_count/self.frames))}|\n" \
                   f"|{' '*left}{time_info}" \
                   f"{' '*right}|\n"
        elif self.frames:
            return f"|{' '*self.width}|\n" \
                   f"|{'>'*round(self.width*(frame_count/self.frames))}" \
                   f"{'-'*round(self.width*(1-frame_count/self.frames))}|\n" \
                   f"|{' '*self.width}|\n"
        else:
            return ""


if __name__ == '__main__':
    print(get_terminal_size())
