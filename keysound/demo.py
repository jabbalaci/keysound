import time


def wait(sec=0.5) -> None:
    time.sleep(sec)


def play_all_sounds(sound) -> None:
    """
    Play all sounds for quickly testing a sound pack and for debugging.
    """
    repeat = 3
    d = {
        "enter": sound.enter,
        "space": sound.space,
        "key_up": sound.key_up,
        "mouse_down": sound.mouse_down,
        "mouse_up": sound.mouse_up,
    }
    print()
    print("buttons with press only (without release):")
    print("------------------------------------------")
    for name, key_obj in d.items():
        print(f"- {name}: {key_obj}")
        for i in range(repeat):
            key_obj.play()
            wait()
        #
        wait(0.6)
    #
    for key in sound.keys:
        print(f"- {key}")
        for i in range(repeat):
            key.play()
            wait()
        #
        wait(0.6)
    #
    print()
    print("buttons with press and release:")
    print("-------------------------------")
    for name, key_obj in d.items():
        if name == "key_up" or name.startswith("mouse"):
            continue
        # else
        print(f"- {name}: {key_obj}")
        for i in range(repeat):
            key_obj.play()
            wait(0.05)
            d["key_up"].play()
            wait()
        #
        wait(0.6)
    #
    for key in sound.keys:
        print(f"- {key}")
        for i in range(repeat):
            key.play()
            wait(0.05)
            d["key_up"].play()
            wait()
        #
        wait(0.6)
    #
    print("- mouse press and release:")
    for i in range(repeat):
        d["mouse_down"].play()
        wait(0.1)
        d["mouse_up"].play()
        wait()
    wait(0.6)
