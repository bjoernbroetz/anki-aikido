# Videos to anki deck

Creates an anki deck based on some videos with aikido techniques.

## Prerequisite

- ffmpeg
- python
  - pyyaml
  - genanki

## Usage

The configuration file `config.yaml` defines the paths to the input files and connects them to the individual configuration files. There is one individual configuration file per input video.    

```
usage: video2anki.py [-h] [-v] [-s] [-d] [--outfile OUTFILE] [--deckid DECKID]

options:
  -h, --help          show this help message and exit
  -v, --verbose       increase output verbosity
  -s, --skipvideocut  skip splitting of videos
  -d, --dryrun        execute script but don't create or change anything
  --outfile OUTFILE   name of the output file. The file extention .apkg will
                      be appended
  --deckid DECKID     id of deck. Default is a random number
```

## Contribution

Contributions are very welcome. When you make adjustment for different input videos, please extent functionality instead replacing functionality so others can build on your contibution. 

## License

MIT License (see LICENSE file)

