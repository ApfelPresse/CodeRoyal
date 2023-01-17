import random

import numpy as np


def predict(inp, tree):
    t = tree[0]
    for v in inp:
        if t[0] <= v:
            idx = int(t[1])
            # t = tree[]
        else:
            idx = int(t[1])
            # t = tree[int(t[2])]
        if idx >= len(tree):
            break
        t = tree[idx]
    return t[3]

def create_full_binary_tree(config):
    depth = config["height"]
    tree = []
    nodes, leaves = get_tree_specs(depth)
    for node in range(nodes):
        p2 = node * 2 + 1
        p3 = node * 2 + 2
        tree.append(create_node(config=config, p2=p2, p3=p3))
    return np.array(tree)


def get_tree_specs(height: int) -> (int, int):
    nodes = 2 ** (height + 1) - 1
    leaves = (nodes + 1) // 2
    return nodes, leaves


def create_node(config, p2=None, p3=None):
    value = random.choice(config["p1_possible_values"])
    if p2 is None:
        p2 = random.choice(config["p2_possible_values"])
    if p3 is None:
        p3 = random.choice(config["p3_possible_values"])
    label = random.choice(config["p4_possible_values"])
    return [value, p2, p3, label]


def create_random_tree(config):
    tree = []
    for _ in range(config["nodes"]):
        tree.append(create_node(config))
    return np.array(tree)


def dna_to_tree(dna):
    return np.array(dna).reshape((-1, 4))


def get_dna(tree):
    a = np.array(tree)
    return a.flatten()
