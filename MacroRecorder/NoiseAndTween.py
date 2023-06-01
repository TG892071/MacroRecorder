import pytweening
import numpy as np
import random


class NoiseAndTween:

    def __init__(self, points, mean=15, std=7, frequency=0.7, target_points=10):
        """
		Class adds noise and fixes the number of coordinates in a list
		"""
        self.mean = mean
        self.std = std
        self.frequency = frequency
        self.points_with_noise_points = self.add_noise_to_points(points)
        self.tweened_points = self.tween_points(points, pytweening.easeOutQuad, target_points)

    def add_noise_to_points(self, points):
        """
        Adds random noise to points in a series of points
        Noise is only added to points on average by the given frequency
        otherwise they will not be changed
        """

        if not isinstance(self.mean, (float, int, np.int32, np.int64, np.float32, np.float64)):
            raise ValueError("Mean must be a number")
        if not isinstance(self.std, (float, int, np.int32, np.int64, np.float32, np.float64)):
            raise ValueError("Standard deviation must be a number")
        if not isinstance(self.frequency, (float, int, np.int32, np.int64, np.float32, np.float64)):
            raise ValueError("Frequency must be a number")
        if not (0 <= self.frequency <= 1):
            raise ValueError("self.frequency must be in range [0,1]")

        points_with_noise = []
        for i in range(1, len(points) - 1):
            x, y = points[i]
            if random.random() < self.frequency:
                change = np.random.normal(self.mean, self.std)
            else:
                change = 0
            points_with_noise += (x, y + change),
        points_with_noise = [points[0]] + points_with_noise + [points[-1]]
        return points_with_noise

    @staticmethod
    def tween_points(points, tween, targetPoints):
        """
        Adds new points between existing points to reach target number of points
        """
        new_points = []
        for i in range(targetPoints):
            tween_value = tween(float(i) / (targetPoints - 1))
            index = int(tween_value * (len(points) - 1))
            new_points.append(points[index])
        return new_points