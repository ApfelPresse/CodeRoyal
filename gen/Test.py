import random
import unittest

import numpy as np

from gen import tree, genetic
from gen.genetic import genetic_algorithm
from gen.tree import predict, get_tree_specs


class Test(unittest.TestCase):

    def test_xor(self):
        def score_xor(args):
            tree, it = args
            predictions = []
            predictions.append(predict(inp=[0, 1], tree=tree) == 1)
            predictions.append(predict(inp=[1, 0], tree=tree) == 1)
            predictions.append(predict(inp=[1, 1], tree=tree) == 0)
            predictions.append(predict(inp=[0, 0], tree=tree) == 0)
            return sum(predictions), tree

        nodes = 2
        n_pop = 10
        config = {
            "n_iter": 50,
            "n_pop": 10,
            "r_cross": 0.4,
            "elite_size": int(n_pop * 0.1),
            "r_mut": 1 / nodes,
            "nodes": nodes,
            "max_score": 4,
            "tree_function": tree.create_random_tree,
            "mutation_function": genetic.mutation_random_tree,
            "crossover_function": genetic.crossover_random,
            "p1_possible_values": [0, 1],
            "p2_possible_values": list(range(nodes)),
            "p3_possible_values": list(range(nodes)),
            "p4_possible_values": [0, 1],
        }
        # with Pool(10) as pool:
        #     pool = None
        best, score = genetic_algorithm(score_xor, config, None)
        print('Done!')
        print(best)
        print(f"Score {score}")

    def test_digits(self):
        from sklearn.datasets import load_digits
        digits = load_digits()
        max_score = 20
        def score_digits(args):
            tree, it = args
            predictions = []
            choices = random.choices(range(digits.data.shape[0]), k=max_score)
            for i in choices:
                predictions.append(
                    predict(inp=list(digits.data[i]), tree=tree) == digits.target[i]
                )
            return sum(predictions), tree

        n_pop = 10
        config = {
            "n_iter": 4000,
            "height": 8,
            "n_pop": n_pop,
            "r_cross": 0.8,
            "elite_size": int(n_pop * 0.2),
            "r_mut": 0.1,
            "max_score": max_score,
            "tree_function": tree.create_full_binary_tree,
            "mutation_function": genetic.mutation_full_binary_tree,
            "crossover_function": genetic.crossover_full_binary_tree,
            "p1_possible_values": list(np.linspace(0, 16, 30)),
            "p4_possible_values": list(range(10)),
        }
        best, score = genetic_algorithm(score_digits, config, None)
        print('Done!')
        print(f"Score {score}/{config['max_score']}")

    def test_max(self):
        def score_xor(args):
            tree, it = args
            predictions = []
            predictions.append(predict(inp=list([0, 1, 2]), tree=tree) == 2)
            predictions.append(predict(inp=list([1, 2, 3]), tree=tree) == 3)
            predictions.append(predict(inp=list([2, 3, 4]), tree=tree) == 4)
            predictions.append(predict(inp=list([3, 4, 5]), tree=tree) == 5)
            predictions.append(predict(inp=list([4, 5, 6]), tree=tree) == 6)
            return sum(predictions), tree

        height = 3
        nodes, leaves = get_tree_specs(height=height)
        n_pop = 100
        config = {
            "n_iter": 4000,
            "n_pop": 100,
            "height": height,
            "r_cross": 0.6,
            "elite_size": int(n_pop * 0.1),
            "r_mut": 1 / nodes,
            "max_score": 5,
            "tree_function": tree.create_full_binary_tree,
            "mutation_function": genetic.mutation_full_binary_tree,
            "crossover_function": genetic.crossover_full_binary_tree,
            "p1_possible_values": [0, 1, 2, 3, 4, 5, 6],
            "p4_possible_values": [2, 3, 4, 5, 6],
        }
        best, score = genetic_algorithm(score_xor, config, None)
        print('Done!')
        print(f"Score {score}")
