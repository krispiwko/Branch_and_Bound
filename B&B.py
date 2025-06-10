import numpy as np

# Klasa opisująca podproblem w branch and bound
class BB_subproblem:
    # Inicjalizacja podproblemu
    def __init__(self, index, reduced_matrix, lower_bound, road_list):
        # Numer identyfikujący podproblem
        self.index = index
        # Zredukowana macierz podproblemu
        self.reduced_matrix = reduced_matrix
        # Ograniczenie dolne
        self.lower_bound = lower_bound
        # Lista przebytych ścieżek
        self.road_list = road_list

    def __str__(self):
        output = "-------"
        output += "Numer: " + str(self.index) + "\n"
        output += "LB: " + str(self.lower_bound) + "\n"
        output += "Obecne rozwiązanie: " + str(self.road_list) + "\n"
        output += "-------"
        return output

    # Znalezienie najlepszej ścieżki dla podproblemu
    def find_best_road(self):
        # Inicjalizacja zmiennych
        max_penalty = -1
        best_road = (-1, -1)
        n = self.reduced_matrix.shape[0]
        # Pętla po każdym elemencie
        for i in range(n):
            for j in range(n):
                # Jeżeli element jest równy zero
                if self.reduced_matrix[i][j] == 0:
                    # Oblicz sumę z minimalnych elementów z wiersza i kolumny (bez zera!)
                    row_vals = [self.reduced_matrix[i][k] for k in range(n) if k != j]
                    col_vals = [self.reduced_matrix[k][j] for k in range(n) if k != i]
                    row_min = min(row_vals) if row_vals else 0
                    col_min = min(col_vals) if col_vals else 0
                    # Obliczona suma to penalty (kara) za wybranie ścieżki
                    penalty = row_min + col_min
                    # Zapamiętaj ścieżkę z największą karą
                    if penalty > max_penalty:
                        max_penalty = penalty
                        best_road = (i, j)
        # Zwracana ścieżka z największą karą
        return best_road

    # Funkcja sprawdzająca, czy wybrana droga nie tworzy podcyklu
    def forms_cycle(self, new_edge):
        # Jeżeli rozwiązanie jest już pełne: zwróć False
        if len(self.road_list) + 1 == self.reduced_matrix.shape[0]:
            return False
        # Stworzenie słownika, w którym każdemu wierzchołkowi
        # przypisujemy wierzchołek końcowy krawędzi ze ścieżki
        path = {a: b for a, b in self.road_list + [new_edge]}
        visited = set()
        # Wybieramy wierzchołek końcowy z dodanej krawędzi jako początkowy
        current = new_edge[1]
        # Dopóki istnieje dalsza ścieżka i obecny wierzchołek nie został odwiedzony
        while current in path and path[current] not in visited:
            # Dodaj wierzchołek do odwiedzonych
            visited.add(current)
            # Zmień wierzchołek na kolejny ze ścieżki
            current = path[current]
        # Jeżeli wróciliśmy się do naszej dodanej krawędzi, to istnieje podcykl
        return current == new_edge[0]

    # Podział podproblemu na dwa
    def divide_subproblem(self):
        solution_with_ban = False
        # Znajdź wierzchołki najlepszej krawędzi
        i, j = self.find_best_road()
        # Sprawdź czy dodanie krawędzi tworzy podcykl
        if self.forms_cycle((i, j)):
            # Jeżeli tak, to nie twórz rozwiązania z krawędzią
            solution_with_ban = True
        n = self.reduced_matrix.shape[0]

        subs = []
        # Tworzenie podproblemu z krawędzią
        if not solution_with_ban:
            matrix_with = np.copy(self.reduced_matrix)
            # Zmień odpowiednie wiersze/ kolumny/ elementy na np.inf dla macierzy z wybraną krawędzią
            matrix_with[i, :] = np.inf
            matrix_with[:, j] = np.inf
            matrix_with[j, i] = np.inf

            # Zredukuj macierz
            reduced_with, red_cost_with = reduce_matrix(matrix_with)
            # Dodaj wybraną krawędź do ścieżki
            road_list_with = self.road_list + [(i, j)]
            subproblem_with = BB_subproblem(
                self.index * 10 + 1, reduced_with,
                self.lower_bound + red_cost_with,
                road_list_with
            )
            subs.append(subproblem_with)
        # Tworzenie podproblemu bez krawędzi
        matrix_without = np.copy(self.reduced_matrix)
        # Zablokuj możliwość wybrania krawędzi (i, j)
        matrix_without[i, j] = np.inf
        # Zredukuj macierz
        reduced_without, red_cost_without = reduce_matrix(matrix_without)
        subproblem_without = BB_subproblem(
            self.index * 10, reduced_without,
            self.lower_bound + red_cost_without,
            self.road_list
        )
        subs.append(subproblem_without)

        return subs

# Klasa reprezentująca cały problem branch and bound
class BB:
    # Inicjalizacja problemu
    def __init__(self, cost_matrix):
        # Macierz kosztów jako np.array
        self.cost_matrix = np.array(cost_matrix)
        # Lista podproblemów
        self.subproblem_list = []
        # Wartość odcinająca (na początku np.inf)
        self.best_v = np.inf
        # Najlepsze rozwiązanie (skojarzone z wartością odcinającą)
        self.best_solution = None
        # Ilość iteracji
        self.iterations = 0
        # Rozmiar problemu
        self.n = len(cost_matrix)

    # Rozwiąż problem branch and bound
    def solve(self):
        # Dalsza inicjalizacja problemu (redukcja, stworzenie pierwszego podproblemu)
        self.initialize()
        # Dopóki istnieje niezamknięty podproblem
        while self.subproblem_list:
            self.iterations += 1
            # Wybierz podproblem o najmniejszym LB
            curr_subproblem = self.choose_subproblem()
            # Spróbuj zamknąć podproblem (jeżeli nie da się zamknąć, to rozdziel na dwa mniejsze)
            self.try_to_close_subproblem(curr_subproblem)
        # Jeżeli znaleziono rozwiązanie optymalne
        if len(self.best_solution) == self.n:
            # Stwórz ścieżkę z wybranych krawędzi
            full_path = self.complete_path(self.best_solution)
            # Wyświetl wynik
            print(f"Optimal TSP cost: {self.best_v}")
            print(f"Optimal path: {self.format_solution(full_path)}")
        else:
            print("No valid solution found!")
        return self.best_v, self.best_solution

    # Stwórz końcową ścieżkę z wybranych krawędzi (nie musi być to
    def complete_path(self, partial_path):
        # Jeżeli ścieżka pusta: zwróć pusty wynik
        if not partial_path:
            return []
        # Stworzenie słownika, w którym każdemu wierzchołkowi
        # przypisujemy wierzchołek końcowy krawędzi ze ścieżki
        path_dict = {i: j for i, j in partial_path}
        # Inicjalizacja zmiennych
        full_path = []
        current = partial_path[0][0]
        visited = set()
        # Dopóki nie zrobimy koła
        while current not in visited:
            # Dodaj do ścieżki krawędź i zmień wierzchołek na kolejny
            visited.add(current)
            next_city = path_dict.get(current)
            full_path.append((current, next_city))
            current = next_city
        return full_path

    # Sformatowanie stworzonej ścieżki do ładnego formatu
    def format_solution(self, solution):
        path = [solution[0][0]]
        for road in solution:
            path.append(road[1])
        return " → ".join(map(str, path))

    # Początkowa inicjalizacja problemu
    def initialize(self):
        # Zredukuj macierz
        matrix, sum_of_reduction = reduce_matrix(self.cost_matrix)
        # Stwórz pierwszy podproblem i dodaj go do listy podproblemów
        first_subproblem = BB_subproblem(1, matrix, sum_of_reduction, [])
        print("Pierwszy podproblem:")
        print(first_subproblem)
        print("Kolejne podproblemy")
        self.subproblem_list.append(first_subproblem)

    # Wybierz podproblem o najmniejszej wartości LB
    def choose_subproblem(self):
        min_idx = min(range(len(self.subproblem_list)), key=lambda i: self.subproblem_list[i].lower_bound)
        return self.subproblem_list.pop(min_idx)

    # Spróbuj zamknąć podproblem
    def try_to_close_subproblem(self, subproblem):
        print(subproblem)
        # KZ1 - brak możliwego rozwiązania (LB == np.inf)
        if subproblem.lower_bound == np.inf:
            print("KZ1!")
            return
        # KZ2 - LB jest większe niż wartość odcinająca
        if subproblem.lower_bound >= self.best_v:
            print("KZ2!")
            return
        # KZ3 - znaleziono wszystkie krawędzie, oprócz ostatniej (problem trywialny)
        if len(subproblem.road_list) == self.n - 1:
            print("KZ3!")
            # Dokończ problem, wybierając jedyną sensowną krawędź
            path = subproblem.road_list.copy()
            all_cities = set(range(self.n))
            sources = set(i for i, j in path)
            dests = set(j for i, j in path)
            missing_source = next(iter(all_cities - sources))
            missing_dest = next(iter(all_cities - dests))
            path.append((missing_source, missing_dest))
            exact_cost = sum(self.cost_matrix[i][j] for i, j in path)
            # Jeżeli obliczony koszt rozwiązania jest mniejszy od wartości odcinającej
            if exact_cost < self.best_v:
                # Uaktualnij wart. odc. i najlepsze rozwiązanie
                self.best_v = exact_cost
                self.best_solution = path
            return
        # Jeżeli nie zadziałało żadne kryterium zamykania: rozdziel podproblem na mniejsze
        subs = subproblem.divide_subproblem()
        for sub in subs:
            self.subproblem_list.append(sub)

# Redukcja macierzy
def reduce_matrix(matrix):
    matrix = np.array(matrix, dtype=float)
    sum_of_reduction = 0
    # Dla każdego wiersza
    for i in range(matrix.shape[0]):
        # Znajdź minimum w wierszu
        row_min = np.min(matrix[i])
        if row_min != np.inf and row_min > 0:
            # Odejmij od każdego elementu w wierszu
            matrix[i] -= row_min
            # Dodaj do zredukowanej sumy
            sum_of_reduction += row_min
    # Dla każdej kolumny
    for j in range(matrix.shape[1]):
        # Znajdź minimum w kolumnie
        col_min = np.min(matrix[:, j])
        if col_min != np.inf and col_min > 0:
            # Odejmij od każdego elementu w kolumnie
            matrix[:, j] -= col_min
            # Dodaj do zredukowanej sumy
            sum_of_reduction += col_min
    # Zwróć macierz i zredukowaną sumę
    return matrix, sum_of_reduction

# Example usage
if __name__ == '__main__':
    n = 6
    # Generowanie symetrycznej macierzy odległości z losowymi wartościami (5-100)
    np.random.seed(42)  # Dla powtarzalności wyników
    distance_matrix = np.random.randint(5, 100, size=(n, n))
    distance_matrix = ((distance_matrix + distance_matrix.T) // 2).astype('float')  # Upewniamy się, że macierz jest symetryczna
    np.fill_diagonal(distance_matrix, np.inf)  # Na przekątnej inf

    # Konwersja do listy list (jeśli potrzebna)
    distance_matrix = distance_matrix.tolist()

    # Wyświetlenie macierzy
    print("Symetryczna macierz odległości (6 miast):")
    for row in distance_matrix:
        print(row)
    tsp_solver = BB(distance_matrix)
    tsp_solver.solve()
