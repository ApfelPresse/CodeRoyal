import random

import numpy as np
import tqdm as tqdm
from numpy.random import rand
from numpy.random import randint

from gen.tree import get_tree_specs


# from . import tree

def selection(pop, res, k=3):
    selection_ix = randint(len(pop))
    for ix in randint(0, len(pop), k - 1):
        score_ix, _ = res[ix]
        score_selection_ix, _ = res[selection_ix]
        if score_ix < score_selection_ix:
            selection_ix = ix
    return pop[selection_ix]


def crossover_full_binary_tree(p1, p2, config):
    r_cross = config["r_cross"]
    c1, c2 = p1.copy(), p2.copy()

    def _cross(p_original, node):
        c = p_original.copy()
        for i, p in enumerate(p_original):
            if p[1] == node or p[2] == node:
                c[i] = p
        return c

    if rand() < r_cross:
        nodes, leaves = get_tree_specs(config["height"])
        node = randint(0, nodes - 1)

        while node <= nodes:
            c1 = _cross(p2, node)
            c2 = _cross(p1, node + 1)

            node = (2 * node) + 1

    return [c1, c2]


def crossover_random(p1, p2, config):
    r_cross = config["r_cross"]
    c1, c2 = p1.copy(), p2.copy()
    if rand() < r_cross:
        pt = randint(0, len(p1))
        c1 = np.concatenate((p1[:pt, :], p2[pt:, :]))
        c2 = np.concatenate((p2[:pt, :], p1[pt:, :]))
    return [c1, c2]


def init_pop(config):
    tree_func = config["tree_function"]
    return [tree_func(config=config) for _ in range(config["n_pop"])]


def genetic_algorithm(objective, config, pool):
    n_iter = config["n_iter"]
    n_pop = config["n_pop"]
    mutation = config["mutation_function"]
    crossover = config["crossover_function"]
    max_score = config["max_score"]

    pop = init_pop(config)
    best_eval = 0
    best, _ = objective((pop[0], 0))
    for it in tqdm.tqdm(range(n_iter)):
        if pool is not None:
            res = pool.map(objective, zip(pop, [it] * n_pop))
        else:
            res = [objective(item) for item in zip(pop, [it] * n_pop)]

        res.sort(key=lambda item: item[0])

        if res[-1][0] > best_eval:
            score, tree = res[-1]
            best, best_eval = tree, score
            print(f"> new best {score}")
            if best_eval >= max_score:
                return [best, best_eval]

        selected = create_population(config, res)

        children = []
        random.shuffle(selected)
        for i in range(0, n_pop, 2):
            p1, p2 = selected[i], selected[i + 1]
            for child in crossover(p1, p2, config):
                children.append(mutation(child, config))
        pop = children
    return [best, best_eval]


def mutation_full_binary_tree(child, config):
    r_mut = config["r_mut"]

    def _mutation(tree_dna, possible_values):
        for i in range(len(tree_dna)):
            if rand() < r_mut:
                tree_dna[i] = random.choice(possible_values)
        return tree_dna

    child[:, 0] = _mutation(child[:, 0], config["p1_possible_values"])
    child[:, 3] = _mutation(child[:, 3], config["p4_possible_values"])
    return child


def mutation_random_tree(child, config):
    r_mut = config["r_mut"]

    def _mutation(tree_dna, possible_values):
        for i in range(len(tree_dna)):
            if rand() < r_mut:
                tree_dna[i] = random.choice(possible_values)
        return tree_dna

    child[:, 0] = _mutation(child[:, 0], config["p1_possible_values"])
    child[:, 1] = _mutation(child[:, 1], config["p2_possible_values"])
    child[:, 2] = _mutation(child[:, 2], config["p3_possible_values"])
    child[:, 3] = _mutation(child[:, 3], config["p4_possible_values"])
    return child


def create_population(config, res):
    selected = []
    selected.extend(map(lambda item: item[1], res[-config["elite_size"]:]))
    selected.extend(init_pop(config)[:-config["elite_size"]])
    return selected
