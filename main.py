#!/usr/bin/env python3

"""
KeySound

Play a sound file when you press a keyboard button.

* https://github.com/jabbalaci/keysound
* by Laszlo Szathmary (jabba.laci@gmail.com), 2024
"""

import argparse
import json
import os
import random
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

from keysound import demo

VERSION = "0.1.11"


# constants
class C(Enum):
    # Priority 1: play with sounddevice+soundfile
    SD_SF = auto()
    # Priority 2: play with simpleaudio
    SA = auto()
    # Priority 3: play in an external process (use this if you have problems with the previous two)
    # this is a fallback solution
    EXTERNAL = auto()


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # root directory of the application

cfg: dict[Any, Any] = {
    "soundpacks": [],  # will be filled later with the folder names in sounds/
    "selected_soundpack": "default",  # may be modified later
    "mouse_clicks": 0,  # 0: no click, 1: click on press, 2: click on press and click on release
    "sounds_base_dir": str(Path(ROOT_DIR, "sounds")),
    "sound_on_key_up": False,  # Do you want sound when you release a button?
}


def get_sounds_dir() -> str:
    path = str(Path(cfg["sounds_base_dir"], cfg["selected_soundpack"]))
    assert os.path.isdir(path)
    return path


def read_keysound_json() -> dict[str, str]:
    try:
        with open(Path(get_sounds_dir(), "keysound.json")) as f:
            return json.load(f)  # type: ignore
        #
    except:
        print("# keysound.json not found or couldn't be read")
        return {}


def process_soundpacks() -> None:
    folders = [
        Path(entry).name
        for entry in glob(f'{cfg["sounds_base_dir"]}/*')
        if os.path.isdir(entry) and not Path(entry).name.startswith("_")
    ]
    cfg["soundpacks"] = folders
    assert cfg["selected_soundpack"] in cfg["soundpacks"], "Non-existing soundpack is selected"
    assert (
        "random" not in cfg["soundpacks"]
    ), "Don't name your soundpack 'random', this name is reserved"


process_soundpacks()


def list_soundpacks() -> None:
    print("Available soundpacks:")
    for sp in sorted(cfg["soundpacks"]):
        print(f"* {sp}")
    #
    print("* random (select a soundpack randomly)")


def select_soundpack(soundpack: str) -> None:
    if soundpack == "random":
        cfg["selected_soundpack"] = random.choice(cfg["soundpacks"])
        return
    # else
    if soundpack not in cfg["soundpacks"]:
        print("Invalid option. ", end="")
        list_soundpacks()
        sys.exit(1)
    # else
    cfg["selected_soundpack"] = soundpack


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
    parser.add_argument(
        "-l",
        "--list",
        action="store_true",
        default=False,
        help="list available soundpacks and exit",
    )
    parser.add_argument(
        "-p",
        "--play-all",
        action="store_true",
        default=False,
        help="play all sound files and exit",
    )
    parser.add_argument("-s", "--sound", help="which soundpack to use")
    parser.add_argument("-m", "--mouse", type=int, help="number of mouse clicks (0, 1 or 2)")
    parser.add_argument(
        "-u",
        "--keyup",
        action="store_true",
        default=False,
        help="make sound when a button is released",
    )
    args = parser.parse_args()
    return args


args = init_argparse()
if args.sound:
    select_soundpack(args.sound)
if args.mouse:
    select_mouse_clicks(args.mouse)
if args.keyup:
    cfg["sound_on_key_up"] = True
if args.list:
    list_soundpacks()
    sys.exit(0)
#


class SoundFile:
    def __init__(self, fname: str, playback=C.SD_SF) -> None:
        """
        Default playback method: sounddevice+soundfile
        It plays most .wav files correctly. If there's a problem with
        a particular .wav file, we can set a different playback method for it.
        """
        sounds_dir = get_sounds_dir()
        self.name = Path(fname).name
        self.fname_with_path = os.path.normpath(Path(sounds_dir, fname))
        self.playback = playback
        self.loaded = False
        self.data = None  # will be set after loading the .wav file
        # special cases

        if self.name.startswith("mouse"):
            self.playback = C.SA
        if sounds_dir.endswith("banana") and self.name.startswith("enter"):
            self.playback = C.EXTERNAL

    def exists(self) -> bool:
        return os.path.isfile(self.fname_with_path)

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

    def __str__(self) -> str:
        result = f"{self.name}"
        return result


class Sound:
    def __init__(self) -> None:
        sounds_dir = get_sounds_dir()
        ks_json = read_keysound_json()
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
        #
        if "mouse_down" in ks_json:
            value = ks_json["mouse_down"]
            self.mouse_down = SoundFile(value)
        if "mouse_up" in ks_json:
            value = ks_json["mouse_up"]
            self.mouse_up = SoundFile(value)
        if "key_up" in ks_json:
            value = ks_json["key_up"]
            self.key_up = SoundFile(value)
        #
        self.check()

    def collect_keys(self) -> list[SoundFile]:
        li = [self.enter, self.space, self.key_up, self.mouse_down, self.mouse_up]
        li.extend(self.keys)
        return li

    def check(self):
        for key in self.collect_keys():
            if not key.exists():
                print(f"Error: {key.fname_with_path} doesn't exist")
                print("Tip: maybe you refer to it from a keysound.json file")
                sys.exit(1)
            #
        #

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
    folder = get_sounds_dir().removeprefix(ROOT_DIR).removeprefix("/")
    print(f"sound pack: {folder}")
    print(f"number of mouse clicks: {cfg['mouse_clicks']}")
    if args.play_all:
        demo.play_all_sounds(sound)
        return
    # else
    print("start typing...")
    with Listener(on_press=on_press, on_release=on_release) as kbd_listener:
        with mouse.Listener(on_click=on_click) as mouse_listener:
            try:
                kbd_listener.join()
                mouse_listener.join()
            except KeyboardInterrupt:
                print()
                sleep(0.15)
        #
    #
    flush_input()


##############################################################################

if __name__ == "__main__":
    main()
