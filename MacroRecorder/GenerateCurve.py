import pyautogui as pg
import numpy as np
import random
from BezierCurve import BezierCurve
class GenerateCurve:

    def __init__(self, end_x, end_y, max_distance=10):
        """
        Generates a human-like set of points on a curve starting at given source point and finishing in a given destination point
        Control points are points which the curves bends towards, creating the more human shape, as opposed to straight lines between points.
        self.points holds the final points generated
        """
        self.start_x = pg.position()[0]
        self.start_y = pg.position()[1]
        self.end_x = end_x
        self.end_y = end_y
        self.max_distance = max_distance
        self.distance = np.sqrt((self.start_x - end_x) ** 2 + (self.start_y - end_y) ** 2)
        self.control_points_number = self.calculate_control_points(self.start_x, self.start_y, self.end_x, self.end_y)
        self.points = self.generate_curve(self.control_points_number)

    @staticmethod
    def calculate_control_points(start_x, start_y, end_x, end_y):
        """
        Calculate the control_points to use in the Bezier curve based on distance and a minimum.
        """
        distance = np.sqrt((start_x - end_x) ** 2 + (start_y - end_y) ** 2)
        cps = round(distance / 180)
        return min(cps, 2)

    def generate_curve(self, control_points_number):
        """
        Generates a curve according to the parameters specified below.
        You can override any of the below parameters. If no parameter is
        passed, the default value is used.
        """
        internal_control_points = self.control_point_coords(control_points_number)
        points = self.generate_points(internal_control_points)
        return points

    def straight_line_check(self):
        """
        Checks if the input coords give a near straight line.
        """
        if (abs(self.start_x - self.end_x) < 20) or (abs(self.start_y - self.end_y) < 20):
            return True
        return False

    def control_point_coords(self, control_points_number):
        """
        Create control points that act as guide/direction of curve.
        Bounded by the mins and maxs so the curve is not too extreme
        """
        if not isinstance(control_points_number, int) or control_points_number < 0:
            raise ValueError("control_points must be non-negative integer")

        points_on_line = []
        for _ in range(control_points_number):
            points_on_line.append(self.pick_coords())

        # Bigger distribution for straight lines as they get curved less on average, very crude way to solev this issue and make almost 0 difference
        if self.straight_line_check():
            max_gauss = 25
        else:
            max_gauss = 15

        control_points = []
        for x, y in points_on_line:
            cpx = x + random.gauss(0, max_gauss)
            cpy = y + random.gauss(0, max_gauss)
            control_points.append((cpx, cpy))

        return control_points

    def pick_coords(self):
        """
        Generates a random control point near the straight line between start and end points.
        """
        # loops for each addition, avoiding duplicates
        x_diff = self.end_x - self.start_x
        y_diff = self.end_y - self.start_y

        x_diff_percent = x_diff / 100
        y_diff_percent = y_diff / 100

        random_number = random.randint(1, 99)
        noise_x = random.randint(round((-(self.distance / 45))) - 1, round(self.distance / 45) + 1)
        noise_y = random.randint(round((-(self.distance / 45))) - 1, round(self.distance / 45) + 1)
        x = (self.start_x + x_diff_percent * random_number) + noise_x
        y = (self.start_y + y_diff_percent * random_number) + noise_y

        return x, y

    def generate_points(self, control_points):
        """
        Generates the points on bezier curve based on pre generated control points passed in.
        """
        x = abs(self.start_x - self.end_x)
        y = abs(self.start_y - self.end_y)
        midPtsCnt = max(x, y, 2)
        control_points = [(self.start_x, self.start_y)] + control_points + [(self.end_x, self.end_y)]
        return BezierCurve.curve_coords(midPtsCnt, control_points)