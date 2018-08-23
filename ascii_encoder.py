import ascii_player
import argparse
import os


def main(args):
    with ascii_player.LiveVideo(args.path, args.resolution, args.fps) as video:
        pass


def get_arguments():
    parser = argparse.ArgumentParser("ascii_encoder.py",
                                     description="Encodes a video to a special ascii format playable byt ascii_player")
    parser.add_argument("path", help="Path to file to encode")
    parser.add_argument("-r", "--resolution", nargs=2, type=int, metavar=("width", "height"),
                        help="rescale the video to width height")
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
