#!/usr/bin/env python3
import numpy
from PIL import Image, ImageOps
import glob
import os
import argparse


class PixelImage:

    def __init__(self, pixels):
        self.pixels = pixels
        self.height, self.width = self.pixels.shape
        self.ascii = []

        for i in range(self.height):
            self.ascii.append([])
            for j in range(self.width):
                self.ascii[i].append(ASCIIImage.get_char(self.pixels[i][j]) * 2)

    def write_to_file(self, path):
        with open(path, "w") as file:
            for i in range(self.height):
                file.write(''.join(self.ascii[i]) + "\n")

    def print(self):
        for i in range(self.height):
            print(''.join(self.ascii[i]))

    char_list = ["#", "@", "0", "$", "%", "/", "(", "!", ";", ",", "-", ".", "`", " "]
    coefficient = len(char_list) / 256

    @staticmethod
    def get_char(colour):
        return ASCIIImage.char_list[int((colour * ASCIIImage.coefficient))]


class ASCIIImage(PixelImage):

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
    parser = argparse.ArgumentParser(prog="ascii_converter.py",
                                     description="Simple image to ascii converter, supports png and jpg files")
    parser.add_argument("source_path",
                        help="path to a file or a directory, if directory all png and jpg files will be converted")
    parser.add_argument("-p", "--print", action="store_true", help="print to stdout instead of saving to a file")
    parser.add_argument("-r", "--resolution", help="rescale the picture to <width>:<height>")
    args = parser.parse_args()

    try:
        res = tuple(map(int, args.resolution.split(":")))
    except ValueError and AttributeError:
        res = None

    if os.path.isdir(args.source_path):
        extensions = ["png", "PNG", "jpg", "JPG", "jpeg", "JPEG"]
        paths = []
        for extension in extensions:
            paths += glob.glob(args.source_path + "/*." + extension)

        for path in paths:
            ascii_image = ASCIIImage(path, res[0], res[1])
            if args.print:
                print(f"{path}:")
                ascii_image.print()
                print()
            else:
                ascii_image.write_to_file(path[:-3] + "txt")
                print(f"Created {path[:-3]+'txt'}")

    elif os.path.isfile(args.source_path):
        ascii_image = ASCIIImage(args.source_path, args.width, args.height)
        if args.print:
            ascii_image.print()
        else:
            ascii_image.write_to_file(args.path[:-3] + "txt")
            print(f"Created {args.path[:-3]+'txt'}")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
