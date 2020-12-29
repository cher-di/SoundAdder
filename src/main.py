import argparse
import prettytable
import re
import progressbar
import os
import datetime
import sys
import typing

import src.audio_adder
import src.utils
import src.status_file
import src.install


progressbar.streams.wrap_stderr()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Program for adding audio to video")

    parser.add_argument("dir_videos",
                        help="Path to directory with videos",
                        type=src.utils.parse_dir_path,
                        metavar="videos")

    parser.add_argument("dir_audios",
                        help="Path to directory with audios",
                        type=src.utils.parse_dir_path,
                        metavar="audios")

    parser.add_argument("dir_results",
                        help="Path to directory to store results",
                        type=src.utils.parse_dir_path,
                        metavar="results")

    parser.add_argument("-y",
                        help="Run script without confirmation prompt",
                        dest="confirm",
                        action="store_true")

    parser.add_argument("-v", "--verbose",
                        help="Activate verbose",
                        dest="verbose",
                        action="store_true")

    parser.add_argument("-s", "--skip",
                        help="Skip failed videos and sounds adding. "
                             "If not specified, exit with first failed adding with return code 1.",
                        dest="skip",
                        action="store_true")

    parser.add_argument("-r", "--report",
                        help="Save report to specified file in json format",
                        dest="status_file",
                        metavar="FILEPATH",
                        type=src.utils.parse_writable_filepath)

    parser.add_argument("-d", "--delta",
                        help="Maximum delta, between durations of video and audio in seconds",
                        dest="delta",
                        type=src.utils.parse_duration_delta,
                        default=0)

    return parser.parse_args()


def run_verbose(runner: src.audio_adder.AudioAdderRunner, num: int) -> int:
    print(f"{num + 1}: {os.path.basename(runner.video_path)} + {os.path.basename(runner.audio_path)}")
    video_length = src.utils.get_media_duration(runner.video_path)
    with progressbar.ProgressBar(max_value=100) as bar:
        for output in runner.run_verbose():
            match = re.search("time=[0-9]{2}:[0-9]{2}:[0-9]{2}", output)
            if match is not None:
                match = match.group(0)
                hours, minutes, seconds = (int(i) for i in match[5:].split(":"))
                time = datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)
                bar.update(int(time / video_length * 100))
    return runner.return_code


def main(runners: typing.Iterable[src.audio_adder.AudioAdderRunner], verbose=False, skip=False,
         status_file_path: str = None) -> int:
    main_returncode = 0
    with src.status_file.StatusFile(status_file_path) as status_file:
        for num, runner in enumerate(runners):
            returncode = run_verbose(runner, num) if verbose else runner.run_silent()
            status_file.add_status(runner.video_path, runner.audio_path, runner.result_path, returncode)
            if returncode:
                print(f'An error occurred when adding {runner.audio_path} to {runner.video_path} '
                      f'and writing to {runner.result_path}, returncode: {returncode}', file=sys.stderr)
                if not skip:
                    return 1
                else:
                    main_returncode = 1
    return main_returncode


def check_requirements():
    if not src.utils.check_ffmpeg_installation():
        src.install.install_ffmpeg()
    if not src.utils.check_ffprobe_installation():
        src.install.install_ffprobe()


if __name__ == '__main__':
    check_requirements()

    args = parse_args()

    print("Scanning directories...")
    audio_adder = src.audio_adder.AudioAdder(args.dir_videos, args.dir_audios, args.dir_results, args.delta)

    correspondence_table = audio_adder.correspondence_table

    table = prettytable.PrettyTable(("#", "Video", "Audio"))
    for num, (video, audio) in enumerate(correspondence_table):
        video_name = os.path.basename(video)
        audio_name = os.path.basename(audio)
        table.add_row((num + 1, video_name, audio_name))
    print(table)
    print(f"Result directory: {args.dir_results}")

    if not args.confirm:
        choice = None
        while choice not in ("y", "n"):
            choice = input("Continue? (y)es/(n)o: ")
        if choice == "n":
            print("Cancellation of program")
        else:
            exit(main(audio_adder.get_runners(), args.verbose, args.skip, args.status_file))
    else:
        exit(main(audio_adder.get_runners(), args.verbose, args.skip, args.status_file))
