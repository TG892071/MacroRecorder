import argparse
import keyboard
import json
from SimpleTimer import SimpleTimer
from pynput import mouse
from pynput import keyboard
from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Listener as KeyboardListener


class MacroRecorder:
    def __init__(self, save_path, save_file, mouse_movement=False):
        """
        Class records macros on a windows PC, both keyboard and mouse inputs.
        Init variables, default list is empty and mouse movements are not recorded by default
        It is recommended not to record mouse movements as outputed files can be very large and playback is less smooth.
        --------
        Args:
        --save_path: String, path to directory where output will be saved
        --save_file: String, file name of save file
        --mouse_movement: Boolean, Determines if we record mouse movements when recording. Default is False/Off
        """
        self.macro_json_list = []
        self.save_path = save_path
        self.save_file = save_file
        self.mouse_movement = mouse_movement

    def __init_controller(self):
        """
        Creates mouse controller
        """
        self.mouse_controller = mouse.Controller()

    def __init_timer(self):
        """
        Starts timer
        """
        self.timer = SimpleTimer()
        self.timer.start()

    def __init_listener(self):
        """
        Creates, starts and join keyboard and mouse listeners for inputs
        """
        self.k_listener = KeyboardListener(on_press=self.on_press, on_release=self.on_release)
        if self.mouse_movement:
            self.m_listener = MouseListener(on_click=self.on_click, on_move=self.on_move)
        else:
            self.m_listener = MouseListener(on_click=self.on_click)
        self.k_listener.start()
        self.m_listener.start()
        self.k_listener.join()
        self.m_listener.join()

    def on_press(self, key):
        """
        Logic for dealing with keyboard key presses
        """
        # Exit for program        
        if key == keyboard.Key.esc:
            self.quit()
            return

        # Assign local variables
        last_json = None
        same_last_action = False

        # If there has been atleast 1 previous action, retrieve it
        if self.macro_json_list:
            last_json = self.macro_json_list[-1]

        # Keys which have "char" attr are dealt with here, eg letters and numbers
        if hasattr(key, "char"):
            # If we are holding down a key the press will be repeatedly heard by listener, we can skip such cases as we record button releases
            if (not (last_json is None)) and ("action" in last_json) and ("key" in last_json):
                last_action = last_json["action"]
                last_key = last_json["key"]

                # Check if last action is same button press
                if last_action == "pressed_key" and last_key == key.char:
                    same_last_action = True

            # If the last action is different, we record newest action.			
            if same_last_action is False:
                x_pos, y_pos = self.mouse_controller.position
                timer = round(self.timer.current_time(), 2)
                self.timer.stop()
                number_rep = ord(key.char)
                if number_rep < 27:
                    json_obj = {"action": "pressed_key", "key": chr(number_rep + 96), "x": x_pos, "y": y_pos,
                                "timer": timer}
                else:
                    json_obj = {"action": "pressed_key", "key": key.char, "x": x_pos, "y": y_pos, "timer": timer}
                self.macro_json_list.append(json_obj)
                self.__init_timer()

        # Keys which have "name" attr are dealt with here, eg special keys such as ctrl, alt, shift and space. Otherwise same as "char" above	
        if hasattr(key, "name"):
            # If we are holding down a key the press will be repeatedly heard by listener, we can skip such cases as we record button releases
            if (not (last_json is None)) and ("action" in last_json) and ("key" in last_json):
                last_action = last_json["action"]
                last_key = last_json["key"]

                # Check if last action is same button press
                if last_action == "pressed_key" and last_key == str(key):
                    same_last_action = True

            # If the last action is different, we record newest action.			
            if same_last_action is False:
                x_pos, y_pos = self.mouse_controller.position
                timer = round(self.timer.current_time(), 2)
                self.timer.stop()
                json_obj = {"action": "pressed_key", "key": str(key), "x": x_pos, "y": y_pos, "timer": timer}
                self.macro_json_list.append(json_obj)
                self.__init_timer()

    def on_release(self, key):
        """
        Logic for dealing with keyboard key releases
        """
        # Deals with release of "char" keys, such as letters and numbers
        if hasattr(key, "char"):
            x_pos, y_pos = self.mouse_controller.position
            current_time = round(self.timer.current_time(), 2)
            self.timer.stop()
            number_rep = ord(key.char)
            if number_rep < 27:
                json_obj = {"action": "released_key", "key": chr(number_rep + 96), "x": x_pos, "y": y_pos,
                            "timer": current_time}
            else:
                json_obj = {"action": "released_key", "key": key.char, "x": x_pos, "y": y_pos, "timer": current_time}
            self.macro_json_list.append(json_obj)
            self.__init_timer()

        # Deals with release of "name" keys, such as ctrl, alt, shift and space. Otherwise same as "char" above
        if hasattr(key, "name"):
            x_pos, y_pos = self.mouse_controller.position
            current_time = round(self.timer.current_time(), 2)
            self.timer.stop()
            json_obj = {"action": "released_key", "key": str(key), "x": x_pos, "y": y_pos, "timer": current_time}
            self.macro_json_list.append(json_obj)
            self.__init_timer()

    def on_click(self, x, y, button, pressed):
        """
        Logic for dealing with mouse button presses and releases
        """
        current_time = round(self.timer.current_time(), 2)
        self.timer.stop()
        json_obj = {"action": "pressed" if pressed else "released", "button": str(button), "x": x, "y": y,
                    "timer": current_time}
        self.macro_json_list.append(json_obj)
        self.__init_timer()

    def on_move(self, x, y):
        """
        Logic for dealing with mouse movements, only recorded if mouse_movement is set to True
        """
        if self.mouse_movement:
            current_time = round(self.timer.current_time(), 2)
            # We only record mouse movements every 0.1 seconds to help prevent massive recording files
            if current_time > 0.1:
                self.timer.stop()
                json_obj = {"action": "moved", "x": x, "y": y, "timer": current_time}
                self.macro_json_list.append(json_obj)
                self.__init_timer()
            else:
                pass

    def run(self):
        """
        Starts recorder 
        """
        # Mouse Controller object
        self.__init_controller()
        # Create timer object and start timer
        self.__init_timer()
        # Set up, start and join listeners for Keyboard and Mouse inputs
        self.__init_listener()

    def quit(self):
        """
        Stops recording and any active timers
        """
        if hasattr(self, "m_listener") and hasattr(self, "k_listener") and hasattr(self, "timer"):
            self.save()
            self.m_listener.stop()
            self.k_listener.stop()
            self.timer.stop()
        else:
            raise Exception("Recorder is not currently running, used the .run() method to begin recording")

    def save(self):
        """
        Saves Json file with keystokes/button presses
        """
        with open(self.save_path + '/{}.txt'.format(self.save_file), 'w+') as outfile:
            json.dump(self.macro_json_list, outfile)


def main(file_path, file_name, mouse_movement):
    r = MacroRecorder(file_path, file_name, mouse_movement)
    r.run()


if __name__ == "__main__":
    argParser = argparse.ArgumentParser()
    argParser.add_argument("--save_path", type=str, required=True, help="String - File path to save directory")
    argParser.add_argument("--save_file", type=str, required=True, help="String - File name for saved macro output")
    argParser.add_argument('--mouse_movement', action='store_true',
                           help="Flag - Allows individual mouse movements to be recorded")
    argParser.add_argument('--no_mouse_movement', dest='mouse_movement', action='store_false',
                           help="Flag - Does not record mouse movements, mouse still moves on key/mouse presses/releases (Recommended option)")
    argParser.set_defaults(mouse_movement=False)
    args = argParser.parse_args()

    main(args.save_path, args.save_file, args.mouse_movement)