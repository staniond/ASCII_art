#!/usr/bin/env python3
import argparse
import os
import subprocess as sp
import time
import json
import sys

import numpy

import ascii_viewer
import util

terminal_size = util.get_terminal_size()


class Video:
    def __init__(self, source, res, fps):
        self.source = source

        info = self.get_info()

        if res is not None:
            self.res = res
        else:
            self.res = info[0], info[1]
        if fps is not None:
            self.fps = fps
        else:
            self.fps = info[2]

        self.frames = info[3]
        self.duration = info[4]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return True

    def get_info(self):
        """Should return tuple - (width, height, fps, frames, duration)"""
        raise NotImplementedError

    def frame_generator(self):
        raise NotImplementedError


class LiveVideo(Video):
    def __init__(self, source, res, fps):
        super().__init__(source, res, fps, )

        if self.source.startswith("http://"):
            time.sleep(.25)

    def frame_generator(self, raw=False):
        frame_command = ["ffmpeg",
                         '-i', self.source,
                         '-f', 'image2pipe',
                         # '-r', f'{self.fps}', # drops or duplicates frames (ffprobe not correct - rip progressbar)
                         '-pix_fmt', 'gray',  # "'-pix_fmt', 'rgb24'," for rgb
                         '-vf', f'scale={self.res[0]}:{self.res[1]}',
                         '-hide_banner',
                         '-sws_flags', 'bicubic',
                         '-vcodec', 'rawvideo', '-']

        # noinspection PyAttributeOutsideInit
        self.pipe = sp.Popen(frame_command, stdout=sp.PIPE, stderr=sp.DEVNULL,
                             bufsize=10 ** 8)

        while True:
            raw_image = self.pipe.stdout.read(self.res[0] * self.res[1])  # * 3 for rgb
            if raw_image == b'':
                return
            if raw:
                yield raw_image
            else:
                pixels = numpy.fromstring(raw_image, dtype='uint8')
                pixels = pixels.reshape((self.res[1], self.res[0]))  # (res[1], res[0], 3) for rgb
                self.pipe.stdout.flush()
                yield pixels

    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self, "pipe"):
            self.pipe.kill()

    def get_info(self):
        command = ["ffprobe",
                   self.source,
                   "-hide_banner",
                   "-select_streams", "v",
                   "-show_entries", "stream=width,height,duration,r_frame_rate,nb_frames",
                   "-show_entries", "format=duration",
                   "-print_format", "json",
                   "-v", "quiet"]
        pipe = sp.Popen(command, stdout=sp.PIPE, stderr=sp.DEVNULL)
        string = pipe.stdout.read().decode()

        info = json.loads(string)
        stream_info = info["streams"][0]
        format_info = info["format"]

        width = stream_info.get("width")
        height = stream_info.get("height")
        try:
            fps = eval(stream_info.get("r_frame_rate"))
        except SyntaxError:
            fps = None
        try:
            frames = int(stream_info.get("nb_frames"))
        except (ValueError, TypeError):
            frames = None

        try:
            if "duration" in stream_info:
                duration = float(stream_info["duration"])
            else:
                duration = float(format_info.get("duration"))
        except (ValueError, TypeError):
            duration = None

        if frames is None and duration is not None:
            frames = int(duration * fps)

        return width, height, fps, frames, duration


class FileVideo(Video):
    # TODO
    def get_info(self):
        pass

    def frame_generator(self):
        pass


def play(video, args, log):
    log.print(
        f"source: {video.source}, resolution: {video.res[0]}x{video.res[1]}px, ({video.res[0]*2}x{video.res[1]}char),"
        f" fps: {video.fps}, frames: {video.frames}, duration: {video.duration}")
    bar = util.ProgressBar(video)

    os.system("clear")

    try:
        start_time = time.time()
        frame_time = 1 / video.fps
        last_time = time.time()
        frame_count = 0

        for frame_pixel_array in video.frame_generator():
            if not args.ignore_fps and ((time.time() - last_time) < frame_time):
                time.sleep(frame_time - (time.time() - last_time))

            last_time = time.time()
            sys.stdout.write('\033[H')
            ascii_viewer.PixelImage(frame_pixel_array).print()
            frame_count += 1

            sys.stdout.write(bar.get_bar(frame_count))
            bot_info = f"{video.source}, " \
                       f"{video.res[0]}x{video.res[1]}px ({video.res[0]*2}x{video.res[1]}char), " \
                       f"frame {frame_count}, " \
                       f"{'%.2f' % (frame_count/(time.time() - start_time))}fps ({video.fps} target)"
            if len(bot_info) < video.res[0] or (terminal_size is not None and len(bot_info) < terminal_size[0]):
                sys.stdout.write(bot_info)

            sys.stdout.flush()
    except KeyboardInterrupt:
        log.print("keyboard interrupt")

    os.system("clear")

    message = f"End of video - {time.time() - start_time}s, {frame_count} frames played," \
              f" {frame_count/(time.time() - start_time)} fps ({video.fps} target)"
    log.print(message)
    print(message)


def main(args):
    log = util.Logger(args.log, "ascii.log")

    if args.path.endswith(".aiv"):
        with FileVideo(args.path, args.resolution, args.fps) as video:
            play(video, args, log)
    else:
        with LiveVideo(args.path, args.resolution, args.fps) as video:
            play(video, args, log)

    if args.log:
        log.log_all(True)


def get_arguments():
    parser = argparse.ArgumentParser("ascii_player.py",
                                     description="Plays video files in terminal using ascii characters")
    parser.add_argument("path", help="Path to file to play")
    parser.add_argument("-i", "--ignore-fps", action="store_true",
                        help="play the video as fast as possible")
    parser.add_argument("-l", "--log", action="store_true",
                        help="save debug info to ascii.log file")
    parser.add_argument("-r", "--resolution", type=int, nargs=2, metavar=("width", "height"),
                        help="rescale the video to width and height")
    parser.add_argument("-f", "--fps", type=int,
                        help="override the fps data found in video")
    args = parser.parse_args()

    if not os.path.isfile(args.path) and not args.path.startswith("http://"):
        print("Provide a valid path to a file")
        print()
        parser.print_help()
        exit(1)

    if not args.resolution:
        if terminal_size is None:
            raise ValueError("Could not get the terminal size. -r flag is required to continue")
        args.resolution = terminal_size[0] // 2, terminal_size[1] - 4

    return args


if __name__ == '__main__':
    main(get_arguments())
