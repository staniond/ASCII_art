#!/usr/bin/env python3
import argparse
import glob
import os
import sys

import numpy
from PIL import Image, ImageOps


class PixelImage:

    def __init__(self, pixels):
        self.pixels = pixels
        self.height, self.width = self.pixels.shape
        self.ascii = []

        for i in range(self.height):
            self.ascii.append([])
            for j in range(self.width):
                self.ascii[i].append(LiveImage.get_char(self.pixels[i][j]) * 2)

    def write_to_file(self, path):
        with open(path, "w") as file:
            for i in range(self.height):
                file.write(''.join(self.ascii[i]) + "\n")  # TODO use string builder
            file.flush()

    def print(self):
        for i in range(self.height):
            sys.stdout.write(''.join(self.ascii[i]) + "\n")  # TODO use string builder

    char_list = ["#", "@", "0", "$", "%", "/", "(", "!", ";", ",", "-", ".", "`", " "]
    coefficient = len(char_list) / 256

    @staticmethod
    def get_char(colour):
        return LiveImage.char_list[int(colour * LiveImage.coefficient)]


class LiveImage(PixelImage):

    def __init__(self, image_path, max_width=424, max_height=140):
        if not os.path.isfile(image_path):
            raise ValueError("provided path is not a path to a file")
        self.image_path = image_path

        image: Image = Image.open(self.image_path)
        image = ImageOps.grayscale(image)
        image.thumbnail((max_width // 2, max_height))
        self.image = image
        super().__init__(numpy.asarray(self.image))


def main():
    parser = argparse.ArgumentParser(prog="ascii_viewer.py",
                                     description="Simple image to ascii converter, supports png and jpg files")
    parser.add_argument("source_path",
                        help="path to a file or a directory, if directory all png and jpg files will be converted")
    parser.add_argument("max_width", type=int,
                        help="rescale the picture to have <max_width>:<max_height> characters (preserves aspect ratio)")
    parser.add_argument("max_height", type=int,
                        help="rescale the picture to <max_width>:<max_height> (preserves aspect ratio)")
    parser.add_argument("-p", "--print", action="store_true", help="print to stdout instead of saving to a file")
    args = parser.parse_args()

    if os.path.isdir(args.source_path):
        extensions = ["png", "PNG", "jpg", "JPG", "jpeg", "JPEG"]
        paths = []
        for extension in extensions:
            paths += glob.glob(args.source_path + "/*." + extension)

        for path in paths:
            ascii_image = LiveImage(path, args.max_width, args.max_height)
            if args.print:
                print(f"{path}:")
                ascii_image.print()
                print()
            else:
                ascii_image.write_to_file(path[:-3] + "txt")
                print(f"Created {path[:-3]+'txt'}")

    elif os.path.isfile(args.source_path):
        ascii_image = LiveImage(args.source_path, args.width, args.height)
        if args.print:
            ascii_image.print()
        else:
            ascii_image.write_to_file(args.path[:-3] + "txt")
            print(f"Created {args.path[:-3]+'txt'}")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
