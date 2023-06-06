# MacroRecorder
Simple Python macro recorder using pynput and pyautogui. Macros are stored as JSON text files in a chosen directory. All keystokes and mouse button pressed are recorded along with current mouse position. The fail safes whilst playing a macro are the pyautogui defaults. Only tested on my local machine running windows 10.

# Usage

## Recording
Run macro recorder from cmd using "python MacroRecorder.py --save_path [PATH] --save_file [FILE_NAME]"
Optional arguments:
* --mouse_movement/--no_mouse_movement, determines if you want mouse movements to be recorded, Default is --no_mouse_movement.

Example:
```
python MacroRecorder.py --save_path C:\ExampleFolder  --save_file ExampleFile --mouse_movement
```

## Playback
Playback a macro recording from cmd using "python MacroPlayer.py --save_path [PATH]  --save_file [FILE_NAME]"
Example: python MacroPlayer.py --save_path C:\ExampleFolder  --save_file ExampleFile.txt --movement_type human
Optional arguments:
* --movement_type [STRING], determines how mouse moves, valid types: "instant", "simple", "human". Default = "human"
* --number_of_plays [NUMBER], determines how many times macro is played back. Default=1
* --max_random_px [NUMBER], determines maximum pixels away from recorded coordinate "human" movement can be. Default=10
* --fail_safe/--no_fail_safe, determines if pyautogui fail safes are on/off. Default is --fail_safe

Example:
```
python MacroPlayer.py --save_path C:\ExampleFolder  --save_file ExampleFile.txt --movement_type human --number_of_plays 2 --max_random_px 5 --fail_safe
```
