# keysound

Play an audio file (a click sound) when a keyboard button is pressed.

## Audio Samples

Soundpacks are located in the `sounds/` folder.
Currently available soundpacks:  
- [samples/default.mp3](samples/default.mp3) (also available on YouTube: [link](https://www.youtube.com/watch?v=fSX_pSVUEUg))
- [samples/fallout.mp3](samples/fallout.mp3) (also available on YouTube: [link](https://www.youtube.com/watch?v=8x_DNb5s65U))
- sounds/banana
- sounds/silver

## Installation

We need the external command `play`, which is
part of the package `sox`. Install it:

```bash
# Ubuntu:
$ sudo apt install sox
# Arch / Manjaro:
$ sudo pacman -S sox
```

`play` is used as a fallback solution. First we
try to play the audio files without external calls.

Then:

- Download the source code
- Create a virtual environment
- Install the requirements (see `pyproject.toml`)

## Usage

- activate the virtual environment
- launch `main.py`

Read the help:

```
$ ./main.py -h
usage: main.py [-h] [-v] [-l] [-p] [-s SOUND] [-m MOUSE] [-u]

Play a sound effect when a keyboard button is pressed

options:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -l, --list            list available soundpacks and exit
  -p, --play-all        play all sound files and exit
  -s SOUND, --sound SOUND
                        which soundpack to use
  -m MOUSE, --mouse MOUSE
                        number of mouse clicks (0, 1 or 2)
  -u, --keyup           make sound when a button is released
```

You can specify the soundpack to be used after `-s`:

```bash
$ ./main.py
$ ./main.py -s fallout
$ ./main.py -s banana
```

## Supported OS

It was tested under **Linux** only (Manjaro Linux). It may (or may not)
work under Windows and MacOS.

## Troubleshoot

Under Ubuntu Linux, you will also need these packages:

```bash
$ sudo apt install libasound2-dev libportaudio2 sox
```

## Credits

The sound files were borrowed from the following
projects:

- https://github.com/zevv/bucklespring
- https://github.com/skkeeper/linux-clicky
- https://mechvibes.com

## Related Work

- https://github.com/zevv/bucklespring
- https://github.com/skkeeper/linux-clicky
- https://github.com/fgheng/keysound
- https://mechvibes.com/
- https://github.com/M1ndo/Neptune
