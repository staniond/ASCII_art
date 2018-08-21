#!/usr/bin/env python3
import argparse
import os
import subprocess as sp
import time

import numpy

import ascii_converter
import util


# TODO kill on keyboard interrupt / other exception
class ASCIIVideo:
    def __init__(self, source, res, fps):
        self.source = source

        info = ASCIIVideo.get_info(source)
        if res is not None:
            self.res = res
        else:
            self.res = info[0]
        if fps is not None:
            self.fps = fps
        else:
            self.fps = info[1]

        self.frame_command = ["ffmpeg",
                              '-i', source,
                              '-f', 'image2pipe',
                              '-pix_fmt', 'gray',  # "'-pix_fmt', 'rgb24'," for rgb
                              '-vf', f'scale={self.res[0]}:{self.res[1]}',
                              '-hide_banner',
                              '-vcodec', 'rawvideo', '-']
        time.sleep(1)

    def frame_generator(self):
        self.pipe = sp.Popen(self.frame_command, stdout=sp.PIPE, bufsize=10 ** 6)

        while True:
            raw_image = self.pipe.stdout.read(self.res[0] * self.res[1] * 1)  # * 3 for rgb
            if raw_image == b'':
                return
            pixels = numpy.fromstring(raw_image, dtype='uint8')
            pixels = pixels.reshape((self.res[1], self.res[0]))  # (res[1], res[0], 3) for rgb
            self.pipe.stdout.flush()
            yield pixels

    def __exit__(self):
        if hasattr(self, "pipe"):
            self.pipe.kill()

    @staticmethod
    def get_info(source):
        command = ["ffprobe",
                   source,
                   "-hide_banner",
                   "-select_streams", "v",
                   "-show_entries", "stream=width,height,r_frame_rate"]
        pipe = sp.Popen(command, stdout=sp.PIPE)
        string = pipe.stdout.read().decode()

        width: int
        height: int
        fps: float
        for line in string.split("\n"):
            if line.startswith("width="):
                width = int(line[6:])
            elif line.startswith("height="):
                height = int(line[7:])
            elif line.startswith("r_frame_rate"):
                fps = eval(line[13:])
        return (width, height), fps


def main(args):
    log = util.Logger()
    try:
        res = tuple(map(int, args.resolution.split(":")))
    except ValueError and AttributeError:
        res = None

    video = ASCIIVideo(args.path, res, args.fps)

    log.print(f"resolution: {video.res[0]}:{video.res[1]}, fps: {video.fps}, source: {video.source}")

    try:
        fps_time = time.time()
        frame_time = 1 / video.fps
        last_time = time.time()
        i = 0

        for frame_pixel_array in video.frame_generator():
            if not args.ignore_fps and ((time.time() - last_time) < frame_time):
                log.print(frame_time - (time.time() - last_time))
                time.sleep(frame_time - (time.time() - last_time))
            last_time = time.time()
            print('\033[1;1H')
            ascii_converter.PixelImage(frame_pixel_array).print()
            i += 1
            print(f"Video from {video.source}, resolution: {video.res[0]}:{video.res[1]}, "
                  f"frame {i}, {i/(time.time() - fps_time)}fps")
    except KeyboardInterrupt:
        pass

    video.__exit__()
    # os.system("clear")
    print(f"End of video - {time.time() - fps_time}s, {i} frames,"
          f" {i/(time.time() - fps_time)} fps ({video.fps} target fps)")

    log.log_all("data/log.txt")


def get_arguments():
    parser = argparse.ArgumentParser("video_converter.py",
                                     description="Plays video files in terminal using ascii characters")
    parser.add_argument("path", help="Path to file to play")
    parser.add_argument("-i", "--ignore-fps", action="store_true",
                        help="play the video as fast as possible")
    parser.add_argument("-r", "--resolution", help="rescale the video to <width>:<height>")
    parser.add_argument("-f", "--fps", type=int,
                        help="override the fps data found in video "
                             "(default 25 if none is found and this option is not specified)")
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    main(get_arguments())
