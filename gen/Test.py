import unittest
from multiprocessing import Pool

import gymnasium as gym
import numpy as np

from gen.genetic import genetic_algorithm


class Test(unittest.TestCase):

    def test_irgendwas(self):
        env = gym.make('MountainCar-v0')
        observation, info = env.reset()

        nodes = observation.shape[0]
        config = {
            "n_iter": 5,
            "n_pop": 100,
            "r_cross": 0.4,
            "elite_size": 10,
            "r_mut": 1 / nodes,
            "nodes": nodes,
            "max_score": 100000000,
            "p1_possible_values": np.linspace(0, 1, num=70),
            "p2_possible_values": list(range(nodes)),
            "p3_possible_values": list(range(nodes)),
            "p4_possible_values": np.linspace(0, 200, num=20),
            "p5_possible_values": list(range(env.action_space.n)),  # labels
        }
        with Pool(10) as pool:
            pool = None
            best, score = genetic_algorithm(Test.mountain_car, config, pool)
        print('Done!')
        print(best)
        print(f"Score {score}")
        Test.mountain_car((best, 0))
        print()

    @staticmethod
    def mountain_car(args):
        tree, it = args

        env = gym.make('MountainCar-v0')
        observation, info = env.reset()

        score = 0
        terminated, truncated = False
        while not terminated and not truncated:
            # for _ in range(1000):

            action = env.action_space.sample()  # agent policy that uses the observation and info
            observation, reward, terminated, truncated, info = env.step(action)

            score += reward
            if terminated or truncated:
                observation, info = env.reset()

        env.close()
        return score, tree
