import argparse

import prettytable
import re
import progressbar
import logging

from src.audio_adder import AudioAdder
from src.utils import measure_time

logging.basicConfig(level=logging.INFO)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Program for adding audio to video")

    parser.add_argument("dir_videos",
                        help="Path to directory with videos")

    parser.add_argument("dir_audios",
                        help="Path to directory with audios")

    parser.add_argument("dir_results",
                        help="Path to directory to store results")

    parser.add_argument("-y",
                        help="Confirm to run script",
                        dest="confirm",
                        action="store_true")

    parser.add_argument("-v", "--verbose",
                        help="Activate verbose",
                        dest="verbose",
                        action="store_true")

    return parser.parse_args()


@measure_time("Add audios to all videos")
def main(audio_adder: AudioAdder, verbose=False):
    import os

    from datetime import timedelta

    from src.utils import get_video_length

    if not verbose:
        for runner in audio_adder.get_runners():
            runner.run_silent()
    else:
        for num, runner in enumerate(audio_adder.get_runners()):
            video = os.path.basename(runner.video_path)
            audio = os.path.basename(runner.audio_path)
            print(f"{num + 1}: {video} + {audio}")

            video_length = int(get_video_length(runner.video_path))
            with progressbar.ProgressBar(max_value=100) as bar:
                for output in runner.run_verbose():
                    match = re.search("time=[0-9]{2}:[0-9]{2}:[0-9]{2}", output)
                    if match is not None:
                        match = match.group(0)
                        hours, minutes, seconds = (int(i) for i in match[5:].split(":"))
                        time = timedelta(hours=hours, minutes=minutes, seconds=seconds)
                        bar.update(int(time.total_seconds() / video_length * 100))


def check_requirements():
    from src.utils import check_ffmpeg_installation, check_ffprobe_installation

    if not check_ffmpeg_installation():
        raise Exception("FFMPEG is not installed")

    if not check_ffprobe_installation():
        raise Exception("FFPROBE is not installed")


if __name__ == '__main__':
    try:
        check_requirements()
    except Exception as e:
        print(e)
        exit(1)

    args = parse_args()

    audio_adder = AudioAdder(args.dir_videos, args.dir_audios, args.dir_results)

    correspondence_table = audio_adder.correspondence_table

    table = prettytable.PrettyTable(("#", "Video", "Audio"))
    for num, (video, audio) in enumerate(correspondence_table):
        table.add_row((num + 1, video, audio))
    print(table)
    print(f"Result directory: {args.dir_results}")

    if not args.confirm:
        choice = None
        while choice not in ("y", "n"):
            choice = input("Continue? (y)es/(n)o: ")
        if choice == "n":
            print("Cancellation of program")
        else:
            main(audio_adder, args.verbose)
    else:
        main(audio_adder, args.verbose)
