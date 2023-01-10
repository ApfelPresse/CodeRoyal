from __future__ import annotations

import math

import numpy as np


# class Distance: << (Vector2.kt : Distance) - IGNORED/Useless


class Vector2:
    """Vector2.kt : Vector2
    """
    x: float
    y: float

    def __init__(self, x: float = 0, y: float = 0):
        self.x = x
        self.y = y

    def snapToIntegers(self):
        return Vector2(round(self.x), round(self.y))

    # TODO Numpy faster numpy.linalg.norm(other-self) ?
    def distanceTo(self, other: Vector2) -> float:
        return np.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)


    def check_if_not_smaller_zero(self):
        if self.x < 0:
            self.x = 0
        if self.y < 0:
            self.y = 0

    def copy(self):
        return Vector2(self.x, self.y)

    def __add__(self, other: Vector2) -> Vector2:
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vector2) -> Vector2:
        return Vector2(self.x - other.x, self.y - other.y)

    def __truediv__(self, value: float):
        x = self.x / value
        y = self.y / value
        return Vector2(x, y)

    def __mul__(self, scalar: float):
        return Vector2(self.x * scalar, self.y * scalar)

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def clampWithin(self, minX: float, maxX: float, minY: float, maxY: float) -> Vector2:
        if self.x < minX:
            nx = minX
        elif self.x > maxX:
            nx = maxX
        else:
            nx = self.x

        if self.y < minY:
            ny = minY
        elif self.y > maxY:
            ny = maxY
        else:
            ny = self.y

        return Vector2(nx, ny)

    def lengthSquared(self):
        return self.x * self.x + self.y * self.y

    def resizedTo(self, newLength):
        return self.normalized() * newLength

    def normalized(self):
        length = math.sqrt(self.lengthSquared())
        if length < 1e-6:
            return Vector2(1, 0)
        return Vector2(self.x / length, self.y / length)

    def towards(self, other: Vector2, maxDistance: float):
        if self.distanceTo(other) < maxDistance:
            return other
        else:
            new_loc = self + (other - self).resizedTo(maxDistance)
            return new_loc
