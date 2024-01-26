import yaml

INFILE = "data/Aikido-Schule_Bodo-Roedel_1-Kyu-Prüfungsprogramm.mp4"

class AikidoTechnique:
    def __init__(self, standing_position, attack, name, start, end):
        self.standing_position = standing_position
        self.attack = attack
        self.name = name
        self.start = start
        self.end = end

    def __str__(self):
        return f"{self.standing_position} - {self.attack} - {self.name} ({self.start} to {self.end})"
    
    def mp4name(self):
        return f"{self.standing_position.replace(' ','-')}_{self.attack.replace(' ','-')}_{self.name.replace(' ','-')}.mp4"

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

def create_ffmpeg_commandline(techniques):
    for technique in aikido_techniques:
        # ffmpeg -i input.mp4 -ss 00:05:10 -to 00:15:30 -c:v copy -c:a copy output2.mp4
        print(f"ffmpeg -i {INFILE} -ss {technique.start} -to {technique.end} -c:v copy -c:a copy {technique.mp4name()}")

if __name__ == "__main__":
    filepath_to_config = "1-kyu_techniken.yaml" 
    yaml_data = read_yaml_file(filepath_to_config)

    aikido_techniques = create_aikido_techniques(yaml_data)
    create_ffmpeg_commandline(aikido_techniques)
