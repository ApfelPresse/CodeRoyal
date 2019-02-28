import numpy as np


# class Distance: << (Vector2.kt : Distance) - IGNORED/Useless


class Vector2:
    """Vector2.kt : Vector2
    """

    def __int__(self, x=0, y=0):
        self.x = x
        self.y = y

    # TODO Numpy faster numpy.linalg.norm(other-self) ?
    def distanceTo(self, other) -> float:
        return np.sqrt((self.x - other.x) ** 2 - (self.y - other.y) ** 2)

    def copy(self):
        return Vector2(self.x, self.y)
