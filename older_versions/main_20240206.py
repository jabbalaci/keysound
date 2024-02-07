#!/usr/bin/env python3

"""
KeySound

Play a sound file when you press a keyboard button.

* https://github.com/jabbalaci/keysound
* by Laszlo Szathmary (jabba.laci@gmail.com), 2024
"""

import os
import sys
from glob import glob
from pathlib import Path
from typing import Any

import simpleaudio as sa
import sounddevice as sd
import soundfile as sf
from pynput import mouse
from pynput.keyboard import Key, Listener

VERSION = "0.1.2"


cfg: dict[Any, Any] = {
    "root": os.path.dirname(os.path.abspath(__file__)),  # root directory of the application
    "soundpacks": ["default", "fallout", "banana"],
    "selected_soundpack_index": 2,  # 0: default, 1: fallout, 2: banana, etc.
    "mouse_clicks": 0,  # 0: no click, 1: click on press, 2: click on press and click on release
    "sounds_base_dir": "sounds",
    "sound_on_key_up": False,  # Do you want sound when you release a button?
}
cfg["sounds_dir"] = str(
    Path(cfg["root"], cfg["sounds_base_dir"], cfg["soundpacks"][cfg["selected_soundpack_index"]])
)


def flush_input() -> None:
    sys.stdin.flush()


def read_sound_file(fname: str):
    # returns a tuple with samples (ndarray) and samplerate (int)
    return sf.read(str(Path(cfg["sounds_dir"], fname)))


class Sound:
    def __init__(self) -> None:
        sounds_dir = cfg["sounds_dir"]
        self.enter = read_sound_file("enter.wav")
        self.space = read_sound_file("space.wav")
        self.keys = [read_sound_file(Path(fname).name) for fname in glob(f"{sounds_dir}/key*.wav")]
        self.key_up = read_sound_file("key_up.wav")
        #
        self.mouse_down = sa.WaveObject.from_wave_file(str(Path(sounds_dir, "mouse_down.wav")))
        self.mouse_up = sa.WaveObject.from_wave_file(str(Path(sounds_dir, "mouse_up.wav")))
        #
        self.prev_key: Key | None = None

    def play(self, audio) -> None:
        sd.play(*audio)
        # sd.wait()  # Wait until sound has finished playing

    def play_sound(self, key: Key) -> None:
        if key == Key.enter:
            audio = sound.enter
        elif key == Key.space:
            audio = sound.space
        else:
            index = abs(hash(key)) % len(self.keys)
            audio = self.keys[index]
        #
        self.play(audio)


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
        sound.play(sound.key_up)


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


def main() -> None:
    folder = cfg["sounds_dir"].removeprefix(cfg["root"]).removeprefix("/")
    print(f"sound pack: {folder}")
    print("start typing...")
    with Listener(on_press=on_press, on_release=on_release) as kbd_listener:
        with mouse.Listener(on_click=on_click) as mouse_listener:
            try:
                kbd_listener.join()
                mouse_listener.join()
            except KeyboardInterrupt:
                print()
        #
    #
    flush_input()


##############################################################################

if __name__ == "__main__":
    main()
