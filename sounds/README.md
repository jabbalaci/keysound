# sound packs

Sound packs are located here.

These sound packs were downloaded from
other sources. See the `_credits.txt`
file in each folder.

If you find a `config.json` file in a folder,
then it was part of the pack. It includes
the author name and source URL.
We don't use this file. Instead, we use `keysound.json`.

## How to add your own sound pack

If you want to add your own sound pack,
then create a subfolder here.

Inside the folder, add these files:

- `enter.wav`, which is played when you hit the Enter
- `space.wav`, which is played when you hit the Space
- `key*.wav`, for all the other buttons
- `keysound.json`, to customize mouse clicks
and the sound of releasing a button

Inside `keysound.json`, only three keys are supported
at the moment: 
`"mouse_down"`, `"mouse_up"` and `"key_up"`. See for
instance `default/keysound.json` for a concrete example.

## Some rules

- the name of the sound pack's subfolder cannot start with
an underscore (`_`) since those folders
will be excluded (keysound will ignore them)

- don't call your subfolder `random` since
this folder name is reserved 
