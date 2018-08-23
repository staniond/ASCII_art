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

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return True

    def get_info(self):
        """Should return tuple - (width, height, fps, frames)"""
        raise NotImplementedError

    def frame_generator(self):
        raise NotImplementedError


class LiveVideo(Video):
    def __init__(self, source, res, fps):
        super().__init__(source, res, fps)
        if self.source.startswith("http://"):
            time.sleep(.25)

        self.frame_command = ["ffmpeg",
                              '-i', source,
                              '-f', 'image2pipe',
                              '-pix_fmt', 'gray',  # "'-pix_fmt', 'rgb24'," for rgb
                              '-vf', f'scale={self.res[0]}:{self.res[1]}',
                              '-hide_banner',
                              '-vcodec', 'rawvideo', '-']

    def frame_generator(self, raw=False):
        # noinspection PyAttributeOutsideInit
        self.pipe = sp.Popen(self.frame_command, stdout=sp.PIPE, stderr=sp.DEVNULL,
                             bufsize=self.res[0] * self.res[1] * 1)

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
                   "-show_entries", "stream=width,height,r_frame_rate,nb_frames",
                   "-print_format", "json",
                   "-v", "quiet"]
        pipe = sp.Popen(command, stdout=sp.PIPE, stderr=sp.DEVNULL)
        string = pipe.stdout.read().decode()

        info = json.loads(string)["streams"][0]

        width = info.get("width")
        height = info.get("height")
        try:
            fps = eval(info.get("r_frame_rate"))
        except SyntaxError:
            fps = None
        try:
            frames = int(info.get("nb_frames"))
        except (ValueError, TypeError):
            frames = None

        return width, height, fps, frames


class FileVideo(Video):
    def get_info(self):
        pass

    def frame_generator(self):
        pass


def play(video, args, log):
    log.print(f"resolution: {video.res[0]}:{video.res[1]}, fps: {video.fps}, source: {video.source}")
    bar = util.ProgressBar(video.res[0], video.frames)

    os.system("clear")

    try:
        fps_time = time.time()
        frame_time = 1 / video.fps
        last_time = time.time()
        i = 0

        for frame_pixel_array in video.frame_generator():
            if not args.ignore_fps and ((time.time() - last_time) < frame_time):
                time.sleep(frame_time - (time.time() - last_time))

            last_time = time.time()
            sys.stdout.write('\033[H')
            ascii_viewer.PixelImage(frame_pixel_array).print()
            i += 1

            sys.stdout.write(bar.get_bar(i))
            sys.stdout.write(
                f"Video from {video.source}, "
                f"resolution: {video.res[0]}x{video.res[1]}px ({video.res[0]*2}x{video.res[1]}char), "
                f"frame {i}, {i/(time.time() - fps_time)}fps      ")
            sys.stdout.flush()
    except KeyboardInterrupt:
        log.print("keyboard interrupt")

    os.system("clear")

    log.print(f"{time.time() - fps_time}s, {i} frames,"
              f" {i/(time.time() - fps_time)} achieved fps")
    print(f"End of video - {time.time() - fps_time}s, {i} frames,"
          f" {i/(time.time() - fps_time)} fps ({video.fps} target fps)")


def main(args):
    log = util.Logger()

    if args.path.endswith(".aiv"):
        with FileVideo(args.path, args.resolution, args.fps) as video:
            play(video, args, log)
    else:
        with LiveVideo(args.path, args.resolution, args.fps) as video:
            play(video, args, log)

    log.log_all("data/log.txt")


def get_arguments():
    parser = argparse.ArgumentParser("ascii_player.py",
                                     description="Plays video files in terminal using ascii characters")
    parser.add_argument("path", help="Path to file to play")
    parser.add_argument("-i", "--ignore-fps", action="store_true",
                        help="play the video as fast as possible")
    parser.add_argument("-r", "--resolution", type=int, nargs=2, metavar=("width", "height"),
                        help="rescale the video to width and height")
    parser.add_argument("-f", "--fps", type=int,
                        help="override the fps data found in video "
                             "(default 25 if none is found and this option is not specified)")
    args = parser.parse_args()

    if not os.path.isfile(args.path) and not args.path.startswith("http://"):
        print("Provide a valid path to a file")
        print()
        parser.print_help()
        exit(1)

    return args


if __name__ == '__main__':
    main(get_arguments())
