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
        pass

    def divide_subproblem(self):
        # Znajdź najlepszą drogę
        # Podziel podproblem na dwa podproblemy
        # Pierwszy podproblem:
        # wykreśl wiersz i i kolumnę j (daj tam np.inf)
        # daj np.inf w polu (j, i)

        # Drugi podproblem:
        # daj np.inf w (i, j)
        # Zwróć oba podproblemy jako obiekty klasy BB_subproblem
        pass


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
            sum_of_reduction = reduce_matrix(curr_subproblem.reduced_matrix)
            self.try_to_close_subproblem(curr_subproblem)



    def initialize(self):
        # Początkowa inicjalizacja problem:
        # daj nieskończoności na przekątnej
        # zredukuj macierz kosztów - dodaj wartość redukcji do lower_bound
        # stwórz obiekt BB_subproblem i dodaj na listę podproblemów
        pass

    def choose_subproblem(self):
        # Wybierz podproblem z listy o najmniejszym lower_bound
        pass

    def try_to_close_subproblem(self, subproblem):
        # Sprawdź kryteria zamknięcia:
        # KZ1 - Brak możliwego rozwiązania (lower_bound == np.inf)
        # KZ2 - Jeżeli lower_bound > best_v
        # KZ3 - Jeżeli znaleziono rozwiązanie v (sprawdzamy czy trzeba zaktualizować best_v)
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
    return sum_of_reduction





