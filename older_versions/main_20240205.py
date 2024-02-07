#!/usr/bin/env python3

"""
KeySound

Play a sound file when you press a keyboard button.

This is the version that I presented in this
video: https://www.youtube.com/watch?v=dI0ut7Sc43c (in Hungarian).

* https://github.com/jabbalaci/keysound
* by Laszlo Szathmary (jabba.laci@gmail.com), 2024
"""

import sys
from glob import glob
from pathlib import Path

import simpleaudio as sa
from pynput import mouse
from pynput.keyboard import Key, Listener

SOUNDS_DIR = "sounds/default"
# SOUNDS_DIR = "sounds/fallout"


def flush_input() -> None:
    sys.stdin.flush()


def read_sound_file(fname: str) -> sa.WaveObject:
    return sa.WaveObject.from_wave_file(str(Path(SOUNDS_DIR, fname)))


class Sound:
    def __init__(self) -> None:
        self.enter = read_sound_file("enter.wav")
        self.space = read_sound_file("space.wav")
        self.keys = [read_sound_file(Path(fname).name) for fname in glob(f"{SOUNDS_DIR}/key*.wav")]
        self.key_up = read_sound_file("key_up.wav")
        self.mouse_down = read_sound_file("mouse_down.wav")
        self.mouse_up = read_sound_file("mouse_up.wav")
        #
        self.prev_key: Key | None = None

    def play(self, wave_obj) -> None:
        play_obj = wave_obj.play()
        # play_obj.wait_done()  # Wait until sound has finished playing

    def play_sound(self, key: Key) -> None:
        if key == Key.enter:
            fname = sound.enter
        elif key == Key.space:
            fname = sound.space
        else:
            index = abs(hash(key)) % len(self.keys)
            fname = self.keys[index]
        #
        self.play(fname)


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
    # sound.play(sound.key_up)


def on_click(x, y, button, pressed) -> None:
    # print("{0} at {1}".format("Pressed" if pressed else "Released", (x, y)))
    # if pressed:
    # sound.play(sound.mouse_down)
    # else:
    # sound.play(sound.mouse_up)
    #
    pass


def main() -> None:
    print(f"sound pack: {SOUNDS_DIR}")
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
