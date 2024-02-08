#!/usr/bin/env python3

"""
KeySound

Play a sound file when you press a keyboard button.

* https://github.com/jabbalaci/keysound
* by Laszlo Szathmary (jabba.laci@gmail.com), 2024
"""

import argparse
import os
import sys
from enum import Enum, auto
from glob import glob
from pathlib import Path
from time import sleep
from typing import Any

import simpleaudio as sa
import sounddevice as sd
import soundfile as sf
from pynput import mouse
from pynput.keyboard import Key, Listener

VERSION = "0.1.6"


# constants
class C(Enum):
    # Priority 1: play with sounddevice+soundfile
    SD_SF = auto()
    # Priority 2: play with simpleaudio
    SA = auto()
    # Priority 3: play in an external process (use this if you have problems with the previous two)
    # this is a fallback solution
    EXTERNAL = auto()


cfg: dict[Any, Any] = {
    "root": os.path.dirname(os.path.abspath(__file__)),  # root directory of the application
    "soundpacks": ["default", "fallout", "banana"],  # in the sounds/ folder
    "selected_soundpack_index": 0,  # 0: default, 1: fallout, 2: banana, etc.
    "mouse_clicks": 0,  # 0: no click, 1: click on press, 2: click on press and click on release
    "sounds_base_dir": "sounds",
    "sound_on_key_up": False,  # Do you want sound when you release a button?
}
cfg["sounds_dir"] = str(
    Path(cfg["root"], cfg["sounds_base_dir"], cfg["soundpacks"][cfg["selected_soundpack_index"]])
)


def select_soundpack(soundpack: str) -> None:
    if soundpack not in cfg["soundpacks"]:
        print("Invalid value. Available soundpacks:")
        for sp in cfg["soundpacks"]:
            print(f"* {sp}")
        #
        sys.exit(1)
    # else
    idx = cfg["soundpacks"].index(soundpack)
    cfg["selected_soundpack_index"] = idx
    cfg["sounds_dir"] = str(Path(cfg["root"], cfg["sounds_base_dir"], soundpack))


def select_mouse_clicks(n: int) -> None:
    if n not in (0, 1, 2):
        print(
            """
Invalid value. Valid options:
* 0 (default, no mouse clicks)
* 1 (click when mouse button pressed)
* 2 (click on press AND click on release)
""".strip()
        )
        sys.exit(1)
    # else
    cfg["mouse_clicks"] = n


def init_argparse() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Play a sound effect when a keyboard button is pressed"
    )
    parser.add_argument("-v", "--version", action="version", version=f"keysound {VERSION}")
    parser.add_argument("-s", "--sound", help="which soundpack to use")
    parser.add_argument("-m", "--mouse", type=int, help="number of mouse clicks (0, 1 or 2)")
    args = parser.parse_args()
    return args


args = init_argparse()
if args.sound:
    select_soundpack(args.sound)
if args.mouse:
    select_mouse_clicks(args.mouse)
#


class SoundFile:
    def __init__(self, fname: str, playback=C.SD_SF) -> None:
        """
        Default playback method: sounddevice+soundfile
        It plays most .wav files correctly. If there's a problem with
        a particular .wav file, we can set a different playback method for it.
        """
        self.fname = fname
        self.fname_with_path = str(Path(cfg["sounds_dir"], fname))
        self.playback = playback
        self.loaded = False
        self.data = None  # will be set after loading the .wav file
        # special cases
        if fname.startswith("mouse"):
            self.playback = C.SA
        if cfg["sounds_dir"].endswith("banana") and fname.startswith("enter"):
            self.playback = C.EXTERNAL

    def _load(self):
        if self.playback == C.SD_SF:
            self.data = sf.read(self.fname_with_path)
        elif self.playback == C.SA:
            self.data = sa.WaveObject.from_wave_file(self.fname_with_path)
        #
        self.loaded = True

    def _play_sound(self):
        if self.playback == C.SD_SF:
            sd.play(*(self.data))
        elif self.playback == C.SA:
            self.data.play()  # type: ignore
        elif self.playback == C.EXTERNAL:
            cmd = f"play -q '{self.fname_with_path}' &"
            os.system(cmd)
        else:
            assert False, "Error: unknown playback method"

    def play(self):
        if not self.loaded:
            self._load()
        #
        self._play_sound()


class Sound:
    def __init__(self) -> None:
        sounds_dir = cfg["sounds_dir"]
        #
        self.enter = SoundFile("enter.wav")
        self.space = SoundFile("space.wav")
        self.keys = [SoundFile(Path(fname).name) for fname in glob(f"{sounds_dir}/key*.wav")]
        self.key_up = SoundFile("key_up.wav")
        #
        self.mouse_down = SoundFile("mouse_down.wav")
        self.mouse_up = SoundFile("mouse_up.wav")
        #
        self.prev_key: Key | None = None

    def play_sound(self, key: Key) -> None:
        if key == Key.enter:
            sound.enter.play()
        elif key == Key.space:
            sound.space.play()
        else:
            index = abs(hash(key)) % len(self.keys)
            audio = self.keys[index]
            audio.play()


sound = Sound()


def on_press(key: Key) -> None:
    # print("{0} pressed".format(key))
    if key == sound.prev_key:
        return
    #
    sound.prev_key = key
    sound.play_sound(key)


def on_release(key: Key) -> None:
    # print("{0} release".format(key))
    # print("---")
    sound.prev_key = None
    if cfg["sound_on_key_up"]:
        sound.key_up.play()


def on_click(x, y, button, pressed) -> None:
    # print("{0} at {1}".format("Pressed" if pressed else "Released", (x, y)))
    clicks = cfg["mouse_clicks"]
    if clicks == 0:
        return
    # else
    if clicks == 1:
        if pressed:
            sound.mouse_down.play()
        #
    elif clicks == 2:
        if pressed:
            sound.mouse_down.play()
        else:  # if released
            sound.mouse_up.play()
        #
    #


def flush_input() -> None:
    sys.stdin.flush()


def main() -> None:
    folder = cfg["sounds_dir"].removeprefix(cfg["root"]).removeprefix("/")
    print(f"sound pack: {folder}")
    print(f"number of mouse clicks: {cfg['mouse_clicks']}")
    print("start typing...")
    with Listener(on_press=on_press, on_release=on_release) as kbd_listener:
        with mouse.Listener(on_click=on_click) as mouse_listener:
            try:
                kbd_listener.join()
                mouse_listener.join()
            except KeyboardInterrupt:
                print()
                sleep(0.1)
        #
    #
    flush_input()


##############################################################################

if __name__ == "__main__":
    main()
