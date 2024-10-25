import yaml
import genanki
import subprocess
import argparse
import random
import logging

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
        return s.replace('ō','o').replace('ū','u')

    def __str__(self):
        return f"{self.standing_position} - {self.attack} - {self.name} ({self.start} to {self.end})"
    
    def mp4name(self):
        return self._clean_makron(f"{self.standing_position}_{self.attack}_{self.name}.mp4").replace(' ','-').replace('(', '+').replace(')', '+')

    def full_name(self):
        return f"{self.standing_position}<br>{self.attack}<br>{self.name}"
    
    def anki_tags(self):
        return self._clean_makron(f"{self.standing_position};{self.attack};{self.name};{self.kyu}").replace(' ', '_').split(';')


def read_yaml_file(file_path):
    with open(file_path, 'r') as file:
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
                        technique['name'],
                        technique['start'],
                        technique['end'],
                        kyu
                    )
                    _techniques.append(instance)

    return _techniques

def split_video_by_techniques(techniques):
    for technique in techniques:
        if technique.start == "00:00:00":
            subprocess.run(["ffmpeg", "-i", f"{INFILE}", "-to", f"{technique.end}", "-vf", "scale=640:-2", "-c:v", "libx264", "-profile:v", "baseline", "-level", "3.0", "-preset", "medium", "-crf", "23", "-movflags", "+faststart", "-an", f"{VIDEO_FOLDER}/{technique.mp4name()}"])
        else:
            subprocess.run(["ffmpeg", "-i", f"{INFILE}", "-ss", f"{technique.start}", "-to", f"{technique.end}", "-vf", "scale=640:-2", "-c:v", "libx264", "-profile:v", "baseline", "-level", "3.0", "-preset", "medium", "-crf", "23", "-movflags", "+faststart", "-an", f"{VIDEO_FOLDER}/{technique.mp4name()}"])


def create_ffmpeg_commandline(techniques):
    """ Deprecated. """
    for technique in techniques:
        if technique.start == "00:00:00":
            print(f"ffmpeg -i {INFILE} -to {technique.end} -c:v copy -c:a copy {technique.mp4name()}")
        else:
            print(f"ffmpeg -i {INFILE} -ss {technique.start} -to {technique.end} -c:v copy -c:a copy {technique.mp4name()}")


def append_to_deck(my_deck, techniques, my_model):
    videos = []
    for technique in techniques: 
        my_note = genanki.Note(model=my_model, fields=[f"{technique.full_name()}", f"[sound:{technique.mp4name()}]"], tags=technique.anki_tags() )
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
        css='.card {font-family: arial;font-size: 40px;text-align: right;color: black;background-color: white;}',
    )

def check_filename(filename):
    """Allow only filenames with alphanumeric values 
    as well as '-' and '_' and of maximum length of 255 characters.
    """
    if filename.replace('-','').replace('_','').isalnum() and len(filename) < 256 :
        return filename
    else:
        raise ValueError('Bad filename.')

def check_id(number):
    """Allow only numeric values of maximum 1e10."""
    if type(number) is int and number < 1e10 :
        return number
    else:
        raise ValueError('Bad deckid.')
        

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-s", "--skipvideocut", help="skip splitting of videos", action="store_true")
    parser.add_argument("-w", "--writecommands", help="write commands to cut the videos to the file XXX", action="store_true")
    parser.add_argument("-d", "--dryrun", help="execute script but don't create or change anything", action="store_true")
    parser.add_argument("--outfile", type=str, default='output', help="name of the output file. The file extention .apkg will be appended")
    parser.add_argument("--deckid", type=int, default=random.randint(int(1e9), int(1e10)), help="id of deck. Default is a random number")

    args = parser.parse_args()

    logger = logging.getLogger('video2anki')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler('logfile.log')
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    if args.verbose:
        ch.setLevel(logging.DEBUG)
    else:
        ch.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)



    description = """<div style="text-align:center;">
Pr&uuml;fungsprogramm der Aikido F&ouml;deration Deutschland.
<b>Videos:</b>
Bodo R&ouml;del  | Aikido Schule K&ouml;ln | <a href="https://www.aikido-schule.de">aikido-schule.de</a>
<b>Code/Issues:</b>
<a href="https://github.com/bjoernbroetz/anki-aikido">github.com/bjoernbroetz/anki-aikido</a>
<svg id="Ebene_1" data-name="Ebene 1" xmlns="http://www.w3.org/2000/svg" width="20%" viewBox="0 0 1890.51 1985.85"><defs><style>.cls-1{fill:#0097c6;}</style></defs><title>-</title><path class="cls-1" d="M1964.58,1520.72c-19.37-507.91-156.5-874-407.61-1088.08-205.35-175.08-435.27-201.23-554.06-201.23-41.76,0-70,3.16-79.66,4.44-13-111.11-83.63-219.21-87.06-224.4l-3.78-5.71-5.79,3.65C392.23,282.75,143.2,587.64,86.41,915.57c-58.74,339.25,114.12,592.07,145.23,634.23-91.47,66.84-150.88,184.25-153.42,189.32l-3.06,6.13,6.06,3.2C387,1909.78,666.1,1991.59,910.7,1991.59c578.87,0,786.35-460.49,804.19-502.9,78.87,35.53,175.92,39.85,218.28,39.85,15.57,0,24.83-.56,24.83-.56l6.84-.41ZM932.32,279.07s13.82,169.16,196.35,280.79C1306.54,668.65,1467,742,1536.81,948.35c12.55,37.09,17.25,70.06,16.84,99-1.07,103.47-67.49,155.1-74.19,157.41-.62.22-.82-.62-.78-2.12-.21-3.13,1.7-11.82,4.25-22.48,1.88-7.77,8.87-49,8.21-103.33-.76-54.7-9.33-122.47-38.69-182.67C1398.17,782.85,1318.8,623,961.6,527.25c0,0-29-79-29.54-219.13Q932,294,932.32,279.07ZM467.71,1375.78s-61.19,73.32-199.54,149c0,0,139.6-97.43,145-311.33,5.27-208.43-11.43-384.08,132.38-547.69,117.85-134.15,243.09-84,250-78.09.25.22.15.49-.11.8l.11.08c1.68,1.45-8.65,4.81-22.3,8.85C757.79,602,614.93,656.16,540,767.25c-49.68,73.66-114.55,171-111.88,352.12,1.14,71.09,12.66,155.07,39.58,255.53a2.49,2.49,0,0,0-.17.21C467.6,1375.33,467.65,1375.55,467.71,1375.78ZM959.37,562.49,1418.09,1357H500.5ZM1334.89,1501c-183.15,99.66-326.9,202-540.65,159.22C623.59,1626.11,601,1498.5,601.56,1483.78a10.12,10.12,0,0,1,.08-1.84c.42-2.19,8.48,5.07,18.8,14.88,11.66,11.08,130,107.69,263.82,117,123.54,8.64,301.66,19.84,563.16-241.66,0,0,94.09,16.35,228.81,98.31C1676.23,1470.5,1522.82,1398.76,1334.89,1501Z" transform="translate(-74.33 -5.74)"/></svg>
<b>AIKIDO</b> F&Ouml;DERATION DEUTSCHLAND e.V.
<a href="https://www.aikido-foederation.de">aikido-foederation.de</a>
</div>
"""
    my_deck = genanki.Deck(check_id(args.deckid), "Aikido techniques with videos.", description)
    my_model = init_anki_model() 
    _videos = []
    for kyu in range(5,0,-1):
        logger.info(f"Processing {kyu} kyu")
        kyu_string = f"{kyu}.kyu"
        INFILE = f"data/Aikido-Schule_Bodo-Roedel_{kyu}-Kyu-Prüfungsprogramm.mp4"
        filepath_to_config = f"{kyu}-kyu_techniken.yaml" 
        yaml_data = read_yaml_file(filepath_to_config)
        aikido_techniques = create_aikido_techniques(yaml_data, kyu_string)
        if args.dryrun:
            logger.info('Preparing dry run by setting option -s and unsetting option -w.')
            setattr(args, 'skipvideocut', True)
            setattr(args, 'writecommands', False)
        else:
            pass
        if args.skipvideocut:
            logger.info('Skipping the splitting of the videos.')
        else:
            logger.info('Starting to split the videos.')
            split_video_by_techniques(aikido_techniques)
        if args.writecommands:
            logger.info('Creating a script with commands for the video cuts.')
            create_ffmpeg_commandline(aikido_techniques)
        else:
            logger.debug('Skip creation of separate script for video cuts.')
        my_deck, videos = append_to_deck(my_deck, aikido_techniques, my_model)
        _videos.extend(videos)
    if args.dryrun:
        logger.info('Dry run: Skipping to write deck to file.')
    else:
        logger.debug('Writing deck to file.')
        create_deck(my_deck, _videos, args.outfile) 
