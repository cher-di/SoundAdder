import argparse

import prettytable
import re
import progressbar

from src.sound_adder import SoundAdder
from src.utils import measure_time


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

    parser.add_argument("-v", "--verbose",
                        help="Activate verbose",
                        dest="verbose",
                        action="store_true")

    return parser.parse_args()


@measure_time("Add sounds to all videos")
def main(sound_adder: SoundAdder, args: argparse.Namespace):
    from src.utils import get_video_length, ffmpeg_time_to_timedelta

    if not args.verbose:
        sound_adder.run()
    else:
        for num, ffmpeg_wrapper in enumerate(sound_adder.get_ffmpeg_wrappers()):
            table = prettytable.PrettyTable(("#", "result"))
            table.add_row((num + 1,
                           ffmpeg_wrapper.result_video_path))
            print(table)

            video_length = get_video_length(ffmpeg_wrapper.video_path, args.ffmpeg_executable)
            with progressbar.ProgressBar(max_value=video_length.total_seconds()) as bar:
                for output in ffmpeg_wrapper.execute_verbose():
                    match = re.search("time=[0-9]{2}:[0-9]{2}:[0-9]{2}", output)
                    if match is not None:
                        match = match.group(0)
                        time = ffmpeg_time_to_timedelta(match[5:])
                        bar.update(time.total_seconds())


if __name__ == '__main__':
    args = parse_args()

    sound_adder = SoundAdder(dir_path_videos=args.dir_videos,
                             dir_path_sounds=args.dir_sounds,
                             dir_path_result=args.dir_results,
                             ffmpeg_executable=args.ffmpeg_executable)

    correspondence_table = sound_adder.correspondence_table

    table = prettytable.PrettyTable(("#", "Video", "Sound"))
    for num, (video, sound) in enumerate(correspondence_table):
        table.add_row((num + 1, video, sound))
    print(table)
    print(f"Result directory: {args.dir_results}")

    if not args.confirm:
        choice = None
        while choice not in ("y", "n"):
            choice = input("Continue? (y)es/(n)o: ")
        if choice == "n":
            print("Cancellation of program")
        else:
            main(sound_adder, args)
    else:
        main(sound_adder, args)
