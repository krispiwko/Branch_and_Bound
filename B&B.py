#!/usr/bin/python
# -*- coding: utf-8 -*-
import numpy as np

import KPiwkowski
import JRymar
import DMałek
class BB_subproblem:

    def __init__(self, index, reduced_matrix, lower_bound, road_list):
        self.index = index
        self.reduced_matrix = reduced_matrix
        self.lower_bound = lower_bound
        self.road_list = road_list

class BB:

    def __init__(self, cost_matrix):
        self.cost_matrix = cost_matrix
        self.subproblem_list = []
        self.best_v = np.inf

    def solve(self):
        pass

    def initialize(self):
        pass

def reduce_matrix(matrix):
    sum_of_reduction = 0
    for i in range(matrix.shape[0]):
        row_min = np.min(matrix, axis=0)[i]
        matrix[i, :] = matrix[i, :] - row_min
        sum_of_reduction += row_min
    for j in range(matrix.shape[1]):
        col_min = np.min(matrix, axis=1)[j]
        matrix[:, j] = matrix[:, j] - col_min
        sum_of_reduction += col_min
    return matrix, sum_of_reduction





