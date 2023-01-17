import unittest

from gen import tree
from gen.genetic import genetic_algorithm
from gen.tree import predict


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

        nodes = 10
        n_pop = 100
        config = {
            "n_iter": 10000,
            "n_pop": 10,
            "r_cross": 0.6,
            "elite_size": int(n_pop * 0.1),
            "r_mut": 1 / nodes,
            "nodes": nodes,
            "max_score": 5,
            "tree_function": tree.create_random_tree,
            "p1_possible_values": [0, 1, 2, 3, 4, 5, 6],
            "p2_possible_values": list(range(nodes)),
            "p3_possible_values": list(range(nodes)),
            "p4_possible_values": [2, 3, 4, 5, 6],
        }
        # with Pool(10) as pool:
        #     pool = None
        best, score = genetic_algorithm(score_xor, config, None)
        print('Done!')
        print(f"Score {score}")
