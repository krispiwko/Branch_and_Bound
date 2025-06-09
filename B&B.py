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

    def find_best_road(self):
        # Znajdź wszystkie wartości minimalne (bez zera!) z wierszy i kolumn z zerami pośrodku
        # Wybierz tę drogę o MASKYMALNEJ wyliczonej wartości
        # Zwraca najlepszą drogę (odcinek (i, j))
        max_penalty = -1
        best_road = (-1, -1)
        n = self.reduced_matrix.shape[0]

        for i in range(n):
            for j in range(n):
                if self.reduced_matrix[i][j] == 0:
                    # Oblicz karę (penalty) za wybranie tej drogi (i, j)
                    row_vals = [self.reduced_matrix[i][k] for k in range(n) if k != j]
                    col_vals = [self.reduced_matrix[k][j] for k in range(n) if k != i]
                    row_min = min(row_vals) if row_vals else 0
                    col_min = min(col_vals) if col_vals else 0
                    penalty = row_min + col_min

                    if penalty > max_penalty:
                        max_penalty = penalty
                        best_road = (i, j)

        return best_road

    def divide_subproblem(self):
        # Znajdź najlepszą drogę
        # Podziel podproblem na dwa podproblemy
        # Pierwszy podproblem:
        # wykreśl wiersz i i kolumnę j (daj tam np.inf)
        # daj np.inf w polu (j, i)

        # Drugi podproblem:
        # daj np.inf w (i, j)
        # Zredukuj oba podproblemy i dodaj do ich LB wartość redukcji
        # Zwróć oba podproblemy jako obiekty klasy BB_subproblem

        i, j = self.find_best_road()
        n = self.reduced_matrix.shape[0]

        # Podproblem z drogą (i, j) WYMUSZONĄ
        matrix_with = np.copy(self.reduced_matrix)
        matrix_with[i, :] = np.inf
        matrix_with[:, j] = np.inf
        matrix_with[j, i] = np.inf  # zapobiega powrotowi

        reduced_with, red_cost_with = reduce_matrix(matrix_with.copy())
        road_list_with = self.road_list + [(i, j)]
        subproblem_with = BB_subproblem(
            self.index + 1, reduced_with,
            self.lower_bound + self.reduced_matrix[i][j] + red_cost_with,
            road_list_with
        )

        # Podproblem z drogą (i, j) ZAKAZANĄ
        matrix_without = np.copy(self.reduced_matrix)
        matrix_without[i, j] = np.inf

        reduced_without, red_cost_without = reduce_matrix(matrix_without.copy())
        subproblem_without = BB_subproblem(
            self.index + 1, reduced_without,
            self.lower_bound + red_cost_without,
            self.road_list
        )

        return subproblem_with, subproblem_without


class BB:

    def __init__(self, cost_matrix):
        self.cost_matrix = cost_matrix
        self.subproblem_list = []
        self.best_v = np.inf

    # K_PIWKOWSKI
    def solve(self):
        # Pętla while self.subproblem_list:
        # jedna metoda grupująca metody algorytmu
        self.initialize()
        while self.subproblem_list:
            curr_subproblem = self.choose_subproblem()
            self.try_to_close_subproblem(curr_subproblem)
        return self.best_v



    def initialize(self):
        # Początkowa inicjalizacja problemu:
        # zredukuj macierz kosztów - dodaj wartość redukcji do lower_bound
        matrix, sum_of_redcution = reduce_matrix(self.cost_matrix)
        # stwórz obiekt BB_subproblem i dodaj na listę podproblemów
        first_subproblem = BB_subproblem(1, matrix, sum_of_redcution, [])
        self.subproblem_list.append(first_subproblem)

    def choose_subproblem(self):
        # Wybierz podproblem z listy o najmniejszym lower_bound (usuń go z listy! np metodą pop())
        return best_subproblem

    def try_to_close_subproblem(self, subproblem):
        # Sprawdź kryteria zamknięcia:
        # KZ1 - Brak możliwego rozwiązania (lower_bound == np.inf)
        # KZ2 - Jeżeli lower_bound > best_v
        # KZ3 - Jeżeli znaleziono rozwiązanie v (rozmiar macierzy <= 2) (sprawdzamy czy trzeba zaktualizować best_v)
        # Jeżeli nic z tego, to dzielimy podproblem i dodajemy dwa te podproblemy do listy
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





