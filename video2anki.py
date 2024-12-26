import argparse
import logging
import random
import subprocess

import genanki
import yaml

VIDEO_FOLDER = "videos"


class AikidoTechnique:
    def __init__(self, standing_position, attack, name, start, end, kyu):
        self.standing_position = standing_position
        self.attack = attack
        self.name = name
        self.start = start
        self.end = end
        self.kyu = kyu

    def _clean_makron(self, s):
        return s.replace("ō", "o").replace("ū", "u")

    def __str__(self):
        return f"{self.standing_position} - {self.attack} - {self.name} ({self.start} to {self.end})"

    def mp4name(self):
        return (
            self._clean_makron(
                f"{self.standing_position}_{self.attack}_{self.name}.mp4"
            )
            .replace(" ", "-")
            .replace("(", "+")
            .replace(")", "+")
        )

    def full_name(self):
        return f"{self.standing_position}<br>{self.attack}<br>{self.name}"

    def anki_tags(self):
        return (
            self._clean_makron(
                f"{self.standing_position};{self.attack};{self.name};{self.kyu}"
            )
            .replace(" ", "_")
            .split(";")
        )


def read_yaml_file(file_path):
    with open(file_path, "r") as file:
        data = yaml.safe_load(file)
    return data


def create_aikido_techniques(yaml_data, kyu):
    _techniques = []

    for standing_position, actions in yaml_data.items():
        for action in actions:
            for attack, techniques in action.items():
                for technique in techniques:
                    instance = AikidoTechnique(
                        standing_position,
                        attack,
                        technique["name"],
                        technique["start"],
                        technique["end"],
                        kyu,
                    )
                    _techniques.append(instance)

    return _techniques


def split_video_by_techniques(techniques, dry_run=False):
    for technique in techniques:
        cmd = [
            "ffmpeg",
            "-i",
            f"{INFILE}",
            "-to",
            "-vf",
            "scale=640:-2",
            "-c:v",
            "libx264",
            "-profile:v",
            "baseline",
            "-level",
            "3.0",
            "-preset",
            "medium",
            "-crf",
            "23",
            "-movflags",
            "+faststart",
            "-an",
        ]
        if technique.start == "00:00:00":
            cmd.insert(4, f"{technique.end}")
            cmd.append(f"{VIDEO_FOLDER}/{technique.mp4name()}")
            # cmd = ["ffmpeg", "-i", f"{INFILE}", "-to", f"{technique.end}", "-vf", "scale=640:-2", "-c:v", "libx264", "-profile:v", "baseline", "-level", "3.0", "-preset", "medium", "-crf", "23", "-movflags", "+faststart", "-an", f"{VIDEO_FOLDER}/{technique.mp4name()}"]
            if dry_run:
                logger.info(f"Dry run: Not executing command: {" ".join(cmd)}")
            else:
                logger.debug(f"Executing command: {" ".join(cmd)}")
                subprocess.run(cmd)
        else:
            cmd.insert(4, f"{technique.end}")
            cmd.insert(3, f"{technique.start}")
            cmd.insert(3, "-ss")
            cmd.append(f"{VIDEO_FOLDER}/{technique.mp4name()}")
            # cmd = ["ffmpeg", "-i", f"{INFILE}", "-ss", f"{technique.start}", "-to", f"{technique.end}", "-vf", "scale=640:-2", "-c:v", "libx264", "-profile:v", "baseline", "-level", "3.0", "-preset", "medium", "-crf", "23", "-movflags", "+faststart", "-an", f"{VIDEO_FOLDER}/{technique.mp4name()}"]
            if dry_run:
                logger.info(f"Dry run: Not executing command: {" ".join(cmd)}")
            else:
                logger.debug(f"Executing command: {" ".join(cmd)}")
                subprocess.run(cmd)


def append_to_deck(my_deck, techniques, my_model):
    videos = []
    for technique in techniques:
        my_note = genanki.Note(
            model=my_model,
            fields=[f"{technique.full_name()}", f"[sound:{technique.mp4name()}]"],
            tags=technique.anki_tags(),
        )
        my_deck.add_note(my_note)
        videos.append(f"{VIDEO_FOLDER}/{technique.mp4name()}")
    return (my_deck, videos)


def create_deck(my_deck, videos, filename):
    filename = check_filename(filename)
    pack = genanki.Package(my_deck)
    pack.media_files = videos
    pack.write_to_file(f"{filename}.apkg")


def init_anki_model():
    return genanki.Model(
        1607392319,
        "Simple Model",
        fields=[
            {"name": "Question"},
            {"name": "MyMedia"},
        ],
        templates=[
            {
                "name": "Card 1",
                "qfmt": "{{Question}}",
                "afmt": '{{FrontSide}}<hr id="answer">{{MyMedia}}',
            },
        ],
        css=".card {font-family: arial;font-size: 40px;text-align: right;color: black;background-color: white;}",
    )


def check_filename(filename):
    """Allow only filenames with alphanumeric values
    as well as '-' and '_' and of maximum length of 255 characters.
    """
    if filename.replace("-", "").replace("_", "").isalnum() and len(filename) < 256:
        return filename
    else:
        raise ValueError("Bad filename.")


def check_id(number):
    """Allow only numeric values of maximum 1e10."""
    if type(number) is int and number < 1e10:
        return number
    else:
        raise ValueError("Bad deckid.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v", "--verbose", help="increase output verbosity", action="store_true"
    )
    parser.add_argument(
        "-s", "--skipvideocut", help="skip splitting of videos", action="store_true"
    )
    parser.add_argument(
        "-d",
        "--dryrun",
        help="execute script but don't create or change anything",
        action="store_true",
    )
    parser.add_argument(
        "--outfile",
        type=str,
        default="output",
        help="name of the output file. The file extention .apkg will be appended",
    )
    parser.add_argument(
        "--deckid",
        type=int,
        default=random.randint(int(1e9), int(1e10)),
        help="id of deck. Default is a random number",
    )

    args = parser.parse_args()

    logger = logging.getLogger("video2anki")
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler("logfile.log")
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    if args.verbose:
        ch.setLevel(logging.DEBUG)
    else:
        ch.setLevel(logging.ERROR)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)

    with open("description.html", "r") as html:
        logger.debug("Read description.")
        description = html.read()

    my_deck = genanki.Deck(
        check_id(args.deckid), "Aikido techniques with videos.", description
    )
    my_model = init_anki_model()
    _videos = []
    for kyu in range(5, 0, -1):
        logger.info(f"Processing {kyu} kyu")
        kyu_string = f"{kyu}.kyu"
        INFILE = f"data/Aikido-Schule_Bodo-Roedel_{kyu}-Kyu-Prüfungsprogramm.mp4"
        filepath_to_config = f"{kyu}-kyu_techniken.yaml"
        yaml_data = read_yaml_file(filepath_to_config)
        aikido_techniques = create_aikido_techniques(yaml_data, kyu_string)
        if args.dryrun:
            logger.info("Preparing dry run by setting option -s.")
            setattr(args, "skipvideocut", True)
        else:
            pass
        if args.skipvideocut:
            logger.info("Skipping the splitting of the videos.")
            split_video_by_techniques(aikido_techniques, dry_run=True)
        else:
            logger.info("Starting to split the videos.")
            split_video_by_techniques(aikido_techniques)
        my_deck, videos = append_to_deck(my_deck, aikido_techniques, my_model)
        _videos.extend(videos)
    if args.dryrun:
        logger.info("Dry run: Skipping to write deck to file.")
    else:
        logger.debug("Writing deck to file.")
        create_deck(my_deck, _videos, args.outfile)
