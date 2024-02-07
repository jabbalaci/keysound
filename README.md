# keysound

Play an audio file (a click sound) when a keyboard button is pressed.

## Audio Samples

Soundpacks are located in the `sounds/` folder.
Currently available soundpacks:  
- [samples/default.mp3](samples/default.mp3) (also available on YouTube: [link](https://www.youtube.com/watch?v=fSX_pSVUEUg))
- [samples/fallout.mp3](samples/fallout.mp3) (also available on YouTube: [link](https://www.youtube.com/watch?v=8x_DNb5s65U))
- sounds/banana

## Installation and Usage

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
- launch `main.py`

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
