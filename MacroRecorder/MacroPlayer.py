import json
import random
import time
import math
import argparse
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController
import pyautogui as pg
from GenerateCurve import GenerateCurve
from NoiseAndTween import NoiseAndTween


class MacroPlayer:
    def __init__(self, save_path, save_file, movement_type="human", number_of_plays=1, max_random_px=10,
                 fail_safe=True):
        """
        Class plays back keyboard and mouse macros recorded using accompanying recorder
        Args:
        --save_path: String, path to directory where input macro is saved
        --save_file: String, file name of macro save file
        --movement_type: String, will determine how mouse is moved. Values are, "instant", "simple", "human"
            --Instant movement there is no travel time.
            --Simple movement there is a straight line movement between current location and destination of cursor
            --Human movement there is a curved movement with some randomness using bezier curve to mimic human-like mouse movements
        --number_of_plays: Int, the macro will be repeated this many times
        --max_random_px: Int, Used when doing human movement type to determine the max distance from actual x and y coords a press can be.
        --fail_safe: Boolean, Will keep standard fail safes for pyautogui, this includes moving mouse to corner of screen and ctrl alt delete to stop running
        """
        pg.FAILSAFE = fail_safe

        valid_movement_type = {"instant", "simple", "human"}
        if movement_type not in valid_movement_type:
            raise ValueError("results: status must be one of %r." % valid_movement_type)

        with open(save_path + '\\' + save_file, "r+") as json_file:
            self.data = json.load(json_file)

        self.mouse = MouseController()
        self.keyboard = KeyboardController()
        self.special_keys = {"Key.shift": Key.shift, "Key.shift_l": Key.shift_r,
                             "Key.tab": Key.tab, "Key.caps_lock": Key.caps_lock, "Key.ctrl_l": Key.ctrl_l,
                             "Key.ctrl_r": Key.ctrl_r, "Key.ctrl": Key.ctrl, "Key.alt": Key.alt, "Key.alt_l": Key.alt_l,
                             "Key.alt_r": Key.alt_r, "Key.cmd": Key.cmd, "Key.cmd_r": Key.cmd_r, "Key.cmd_l": Key.cmd_l,
                             "Key.enter": Key.enter, "Key.backspace": Key.backspace, "Key.f20": Key.f20,
                             "Key.f19": Key.f19, "Key.f18": Key.f18, "Key.f17": Key.f17, "Key.f16": Key.f16,
                             "Key.f15": Key.f15, "Key.f14": Key.f14, "Key.f13": Key.f13, "Key.f12": Key.f12,
                             "Key.f11": Key.f11, "Key.f10": Key.f10, "Key.f9": Key.f9, "Key.f8": Key.f8,
                             "Key.f7": Key.f7, "Key.f6": Key.f6, "Key.f5": Key.f5, "Key.f4": Key.f4, "Key.f3": Key.f3,
                             "Key.f2": Key.f2, "Key.f1": Key.f1, "Key.media_volume_up": Key.media_volume_up,
                             "Key.media_volume_down": Key.media_volume_down,
                             "Key.media_volume_mute": Key.media_volume_mute,
                             "Key.media_play_pause": Key.media_play_pause, "Key.right": Key.right, "Key.down": Key.down, "Key.left": Key.left, "Key.up": Key.up,
                             "Key.page_up": Key.page_up, "Key.page_down": Key.page_down, "Key.home": Key.home,
                             "Key.end": Key.end, "Key.delete": Key.delete, "Key.space": Key.space}
        self.number_of_plays = number_of_plays
        self.movement_type = movement_type
        self.max_random_px = max_random_px

    def run(self):
        """
        Main Loop for running macro
        """
        for loop in range(self.number_of_plays):
            for index, obj in enumerate(self.data):
                action, timer, x, y = obj['action'], obj['timer'], obj['x'], obj['y']

                # If cursor hasn't moved we just sleep until action
                if x == pg.position()[0] and y == pg.position()[1]:
                    time.sleep(timer)

                # If we have a "moved" action we just use simple movement
                elif action == "moved":
                    self.simple_movement(x, y, timer)

                # For all other actions we use inputted movement type
                else:
                    if self.movement_type == "instant":
                        self.instant_movement(x, y, timer)
                    if self.movement_type == "simple":
                        self.simple_movement(x, y, timer)
                    if self.movement_type == "human":
                        # Add randomness for human like movements start and end points
                        if self.max_random_px > 0:
                            x_randomness = random.randint(-self.max_random_px, self.max_random_px)
                            y_randomness = random.randint(-self.max_random_px, self.max_random_px)
                            self.human_movement(x + x_randomness, y + y_randomness, timer)
                        else:
                            self.human_movement(x, y, timer)

                # Keys presses from keyboard
                if action == "pressed_key" or action == "released_key":
                    key = obj['key'] if 'Key.' not in obj['key'] else self.special_keys[obj['key']]

                    if action == "pressed_key":
                        self.keyboard.press(key)
                    else:
                        self.keyboard.release(key)

                # Mouse actions, press and release
                if action == "pressed" or action == "released":
                    button = obj['button']
                    split = button.split(".")
                    button_enum = getattr(Button, split[1])

                    if action == "pressed":
                        self.mouse.press(button_enum)
                    if action == "released":
                        self.mouse.release(button_enum)
    @staticmethod
    def instant_movement(x, y, timer):
        """
        Instant movement function, we take 0.2 seconds of sleep timer for processing overhead to keep us more consistent.
        """
        pg.PAUSE = 0.00
        pg.moveTo(x, y)
        overhead = 0.2
        if timer - overhead > 0:
            time.sleep(timer - overhead)
        else:
            pass

    @staticmethod
    def simple_movement(x, y, timer):
        """
        Simple movement function, Quick movements are done with minimal travel time.
        """
        pg.PAUSE = 0.00
        if timer > 0.2:
            if timer < 0.7:
                pg.moveTo(x, y, (timer - 0.2))
            else:
                travel_time = random.uniform(0.3, 0.7)
                wait_time = timer - travel_time
                pg.moveTo(x, y, travel_time)
                time.sleep(wait_time)
        else:
            pg.moveTo(x, y, 0.001)

    @staticmethod
    def human_movement(x, y, timer):
        """
        Human movement function, uses bezier curve and noise/tween generating classes to achieve movement points.
        """
        if timer > 0.7:
            time.sleep(timer - 0.6)
            timer = timer - (timer - 0.7)
        number_of_points = math.floor(timer / 0.03)

        if number_of_points > 5:
            curve = GenerateCurve(x, y)
            tweened_curve = NoiseAndTween(curve.points, target_points=number_of_points)
            for point in tweened_curve.tweened_points:
                pg.PAUSE = 0.02
                pg.moveTo(point[0], point[1])
        else:
            pg.moveTo(x, y, timer, pg.easeOutQuad)


def main(file_path, file_name, movement_type, number_of_plays, max_random_px, fail_safe):
    r = MacroPlayer(file_path, file_name, movement_type, number_of_plays, max_random_px, fail_safe)
    r.run()


if __name__ == "__main__":
    argParser = argparse.ArgumentParser()
    argParser.add_argument("--save_path", type=str, required=True, help="String - File path to save directory")
    argParser.add_argument("--save_file", type=str, required=True, help="String - File name for saved macro input")
    argParser.add_argument("--movement_type", type=str, required=True, help="String - Determine mouse movement type must be 'instant','simple' or 'human'")
    argParser.add_argument("--number_of_plays", type=int, required=False, help="Integer - Number of times to play macro")
    argParser.add_argument("--max_random_px", type=str, required=False, help="String - File name for saved macro input")
    argParser.add_argument('--fail_safe', action='store_true', help="Flag - Keeps pyautogui fail safes")
    argParser.add_argument('--no_fail_safe', dest='fail_safe', action='store_false', help="Flag - Turns off pyautogui fail safes (NOT RECOMMENDED)")
    argParser.set_defaults(number_of_plays=1, max_random_px=10, fail_safe=True)
    args = argParser.parse_args()

    main(args.save_path, args.save_file, args.movement_type,args.number_of_plays, args.max_random_px, args.fail_safe)
