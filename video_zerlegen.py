import yaml
import genanki
import subprocess

VIDEO_FOLDER = "videos"

class AikidoTechnique:
    def __init__(self, standing_position, attack, name, start, end):
        self.standing_position = standing_position
        self.attack = attack
        self.name = name
        self.start = start
        self.end = end
     
    def _clean_makron(self, s):
        return s.replace('ō','o').replace('ū','u')

    def __str__(self):
        return f"{self.standing_position} - {self.attack} - {self.name} ({self.start} to {self.end})"
    
    def mp4name(self):
        return self._clean_makron(f"{self.standing_position}_{self.attack}_{self.name}.mp4").replace(' ','-').replace('(', '+').replace(')', '+')

    def full_name(self):
        return f"{self.standing_position} {self.attack} {self.name}"
    
    def anki_tags(self):
        return self._clean_makron(f"{self.standing_position} {self.attack} {self.name}").replace('(', ' ').replace(')', ' ').split()


def read_yaml_file(file_path):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
    return data


def create_aikido_techniques(yaml_data):
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
                        technique['end']
                    )
                    _techniques.append(instance)

    return _techniques

def split_video_by_techniques(techniques):
    for technique in techniques:
        # ffmpeg -i input.mp4 -ss 00:05:10 -to 00:15:30 -c:v copy -c:a copy output2.mp4

        # ffmpeg -i Aikido-Schule_Bodo-Roedel_1-Kyu-Prüfungsprogramm.mp4 -ss 00:05:10 -to 00:05:30 -vf scale=640:-2 -c:v libx264 -profile:v baseline -level 3.0 -preset medium -crf 23 -movflags +faststart -an chat_buddy_noaudio_mobile_reduced.mp4
        if technique.start == "00:00:00":
            subprocess.run(["ffmpeg", "-i", f"{INFILE}", "-to", f"{technique.end}", "-vf", "scale=640:-2", "-c:v", "libx264", "-profile:v", "baseline", "-level", "3.0", "-preset", "medium", "-crf", "23", "-movflags", "+faststart", "-an", f"{VIDEO_FOLDER}/{technique.mp4name()}"])
        else:
            subprocess.run(["ffmpeg", "-i", f"{INFILE}", "-ss", f"{technique.start}", "-to", f"{technique.end}", "-vf", "scale=640:-2", "-c:v", "libx264", "-profile:v", "baseline", "-level", "3.0", "-preset", "medium", "-crf", "23", "-movflags", "+faststart", "-an", f"{VIDEO_FOLDER}/{technique.mp4name()}"])


def create_ffmpeg_commandline(techniques):
    """ Deprecated. """
    for technique in techniques:
        # ffmpeg -i input.mp4 -ss 00:05:10 -to 00:15:30 -c:v copy -c:a copy output2.mp4
        if technique.start == "00:00:00":
            print(f"ffmpeg -i {INFILE} -to {technique.end} -c:v copy -c:a copy {technique.mp4name()}")
        else:
            print(f"ffmpeg -i {INFILE} -ss {technique.start} -to {technique.end} -c:v copy -c:a copy {technique.mp4name()}")


def append_to_deck(my_deck, techniques, my_model):
    videos = []
    for technique in techniques: 
        my_note = genanki.Note(model=my_model, fields=[f"{technique.full_name()}", f"[sound:{technique.mp4name()}]"])
        my_deck.add_note(my_note)
        videos.append(f"{VIDEO_FOLDER}/{technique.mp4name()}")
    return (my_deck, videos)

 
def create_deck(my_deck, videos):
    pack = genanki.Package(my_deck)
    pack.media_files = videos
    pack.write_to_file("output.apkg")


def init_anki_model():
    return genanki.Model(
        1607392319,
        "Simple Model",
        fields=[
            {"name": "Question"},
            #{"name": "Answer"},
            {"name": "MyMedia"},
        ],
        templates=[
            {
                "name": "Card 1",
                "qfmt": "{{Question}}",
                "afmt": '{{FrontSide}}<hr id="answer">{{MyMedia}}',
            },
        ],
    )

if __name__ == "__main__":

    my_deck = genanki.Deck(2059400110, "Aikido Bodo")
    my_model = init_anki_model() 
    _videos = []
    for kyu in range(5,0,-1):
        print(kyu)
        INFILE = f"data/Aikido-Schule_Bodo-Roedel_{kyu}-Kyu-Prüfungsprogramm.mp4"
        filepath_to_config = f"{kyu}-kyu_techniken.yaml" 
        yaml_data = read_yaml_file(filepath_to_config)
        aikido_techniques = create_aikido_techniques(yaml_data)
        split_video_by_techniques(aikido_techniques)
        #create_ffmpeg_commandline(aikido_techniques)
        my_deck, videos = append_to_deck(my_deck, aikido_techniques, my_model)
        _videos.extend(videos)
    # write deck to file
    create_deck(my_deck, _videos) 

