import random

import numpy as np


def predict(inp, tree):
    t = tree[0, :]
    for v in inp:
        if t[0] <= v:
            t = tree[int(t[1]), :]
        else:
            t = tree[int(t[2]), :]
    return t[3]


def create_tree(config):
    tree = []
    for _ in range(config["nodes"]):
        value = random.choices(config["p1_possible_values"])
        p2 = random.choices(config["p2_possible_values"])
        p3 = random.choices(config["p3_possible_values"])
        p4 = random.choices(config["p4_possible_values"])
        tree.append([value, p2, p3, p4])
    return np.array(tree)


def dna_to_tree(dna):
    return np.array(dna).reshape((-1, 4))


def get_dna(tree):
    a = np.array(tree)
    return a.flatten()
