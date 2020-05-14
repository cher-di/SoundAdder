import argparse
import prettytable

from src.sound_adder import SoundAdder


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Program for adding sound to video")

    parser.add_argument("dir_videos",
                        help="Path to directory with videos")

    parser.add_argument("dir_sounds",
                        help="Path to directory with sounds")

    parser.add_argument("dir_results",
                        help="Path to directory to store results")

    parser.add_argument("-y",
                        help="Confirm to run script",
                        dest="confirm",
                        action="store_true")

    parser.add_argument("-e", "--exe",
                        help="Path to ffmpeg executable",
                        dest="ffmpeg_executable",
                        default="ffmpeg")

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    sound_adder = SoundAdder(dir_path_videos=args.dir_videos,
                             dir_path_sounds=args.dir_sounds,
                             dir_path_result=args.dir_results,
                             ffmpeg_executable=args.ffmpeg_executable)

    correspondence_table = sound_adder.correspondence_table

    table = prettytable.PrettyTable(("#V", "Video", "#S", "Sound"))
    for _num, (video, sound) in enumerate(correspondence_table):
        num = _num + 1
        table.add_row((num, video, num, sound))
    print(table)
    print(f"Result directory: {args.dir_results}")

    if not args.confirm:
        choice = None
        while choice not in ("y", "n"):
            choice = input("Continue? (y)es/(n)o: ")
        if choice == "n":
            print("Cancellation of program")
        else:
            sound_adder.run()
    else:
        sound_adder.run()
