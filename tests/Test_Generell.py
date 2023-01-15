import random
import unittest

import numpy as np

from original.ref import Referee


class Test(unittest.TestCase):

    def setUp(self):
        seed_value = 6
        random.seed(seed_value)
        np.random.seed(seed_value)

    def test_multiple_refs(self):
        ref = Referee(params={
            "leagueLevel": 3
        })
        ref = Referee(params={
            "leagueLevel": 3
        })