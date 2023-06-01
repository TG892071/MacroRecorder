import math
class BezierCurve:
    @staticmethod
    def bernstein_polynomial_point(x, k, n):
        """Calculate the k-th point for the n-th degree,
        n being the number of points
        """
        return math.comb(n, k) * (x ** k) * ((1 - x) ** (n - k))

    @staticmethod
    def bernstein_polynomial(coords, x):
        """
        Given list of control coords and x, returns a point on the bezier curve,
        based on input coords. X is denotes the progress between 0 and 1 of how
        far along the curve the current point is.
        """
        n = len(coords) - 1
        point_x = 0
        point_y = 0
        for k, coord in enumerate(coords):
            bern = BezierCurve.bernstein_polynomial_point(x, k, n)
            point_x += coord[0] * bern
            point_y += coord[1] * bern
        return point_x, point_y

    @staticmethod
    def curve_coords(n, coords):
        """
        Given list of normal coords and current progress along curve,
        returns coords that match bezier curve.
        """
        curvecoords = []
        for i in range(n):
            x = i / (n - 1)
            curvecoords.append(BezierCurve.bernstein_polynomial(coords, x))
        return curvecoords