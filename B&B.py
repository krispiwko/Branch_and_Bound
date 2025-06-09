import numpy as np

class BB_subproblem:
    def __init__(self, index, reduced_matrix, lower_bound, road_list, cost_matrix):
        self.index = index
        self.reduced_matrix = reduced_matrix
        self.lower_bound = lower_bound
        self.road_list = road_list
        self.cost_matrix = cost_matrix

    def find_best_road(self):
        max_penalty = -1
        best_road = (-1, -1)
        n = self.reduced_matrix.shape[0]

        for i in range(n):
            for j in range(n):
                if self.reduced_matrix[i][j] == 0:
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
        i, j = self.find_best_road()
        n = self.reduced_matrix.shape[0]

        matrix_with = np.copy(self.reduced_matrix)
        matrix_with[i, :] = np.inf
        matrix_with[:, j] = np.inf
        matrix_with[j, i] = np.inf

        def forms_cycle(road_list, new_edge):
            path = {a: b for a, b in road_list + [new_edge]}
            visited = set()
            current = new_edge[1]
            while current in path and current not in visited:
                visited.add(current)
                current = path[current]
            return current == new_edge[0] and len(visited) < len(road_list) + 1

        if forms_cycle(self.road_list, (i, j)):
            matrix_with[i, j] = np.inf

        reduced_with, red_cost_with = reduce_matrix(matrix_with)
        road_list_with = self.road_list + [(i, j)]
        subproblem_with = BB_subproblem(
            self.index + 1, reduced_with,
            self.lower_bound + red_cost_with,
            road_list_with, self.cost_matrix
        )

        matrix_without = np.copy(self.reduced_matrix)
        matrix_without[i, j] = np.inf
        reduced_without, red_cost_without = reduce_matrix(matrix_without)
        subproblem_without = BB_subproblem(
            self.index + 1, reduced_without,
            self.lower_bound + red_cost_without,
            self.road_list, self.cost_matrix
        )

        return subproblem_with, subproblem_without

class BB:
    def __init__(self, cost_matrix):
        self.cost_matrix = np.array(cost_matrix)
        self.subproblem_list = []
        self.best_v = np.inf
        self.best_solution = None
        self.iterations = 0
        self.n = len(cost_matrix)

    def solve(self):
        self.initialize()
        while self.subproblem_list:
            self.iterations += 1
            curr_subproblem = self.choose_subproblem()
            self.try_to_close_subproblem(curr_subproblem)

        if self.best_solution is not None:
            full_path = self.complete_path(self.best_solution)
            print(f"Optimal TSP cost: {self.best_v}")
            print(f"Optimal path: {self.format_solution(full_path)}")
        else:
            print("No valid solution found!")
        return self.best_v

    def complete_path(self, partial_path):
        if not partial_path:
            return []
        path_dict = {i: j for i, j in partial_path}
        start = next(iter(set(path_dict.keys()) - set(path_dict.values())), partial_path[0][0])
        full_path = []
        current = start
        visited = set()
        while current not in visited and len(full_path) < self.n:
            visited.add(current)
            next_city = path_dict.get(current)
            if next_city is not None:
                full_path.append((current, next_city))
                current = next_city
            else:
                break
        if full_path and full_path[-1][1] != full_path[0][0]:
            full_path.append((full_path[-1][1], full_path[0][0]))
        return full_path

    def format_solution(self, solution):
        if not solution:
            return "No solution found"
        path = [solution[0][0]]
        for road in solution:
            path.append(road[1])
        return " → ".join(map(str, path))

    def initialize(self):
        matrix, sum_of_reduction = reduce_matrix(self.cost_matrix)
        first_subproblem = BB_subproblem(1, matrix, sum_of_reduction, [], self.cost_matrix)
        self.subproblem_list.append(first_subproblem)

    def choose_subproblem(self):
        min_idx = min(range(len(self.subproblem_list)), key=lambda i: self.subproblem_list[i].lower_bound)
        return self.subproblem_list.pop(min_idx)

    def try_to_close_subproblem(self, subproblem):
        if subproblem.lower_bound == np.inf:
            return
        if subproblem.lower_bound >= self.best_v:
            return
        if len(subproblem.road_list) == self.n - 1:
            path = subproblem.road_list.copy()
            all_cities = set(range(self.n))
            sources = set(i for i, j in path)
            dests = set(j for i, j in path)
            missing_source = next(iter(all_cities - sources))
            missing_dest = next(iter(all_cities - dests))
            path.append((missing_source, missing_dest))
            exact_cost = sum(self.cost_matrix[i][j] for i, j in path)
            if exact_cost < self.best_v:
                self.best_v = exact_cost
                self.best_solution = path
            return
        sub_with, sub_without = subproblem.divide_subproblem()
        self.subproblem_list.append(sub_with)
        self.subproblem_list.append(sub_without)

def reduce_matrix(matrix):
    matrix = np.array(matrix, dtype=float)
    sum_of_reduction = 0
    for i in range(matrix.shape[0]):
        row_min = np.min(matrix[i])
        if row_min != np.inf and row_min > 0:
            matrix[i] -= row_min
            sum_of_reduction += row_min
    for j in range(matrix.shape[1]):
        col_min = np.min(matrix[:, j])
        if col_min != np.inf and col_min > 0:
            matrix[:, j] -= col_min
            sum_of_reduction += col_min
    return matrix, sum_of_reduction

# Example usage
if __name__ == '__main__':
    cost_matrix = [
        [np.inf, 10, 15, 20],
        [10, np.inf, 35, 25],
        [15, 35, np.inf, 30],
        [20, 25, 30, np.inf]
    ]

    tsp_solver = BB(cost_matrix)
    tsp_solver.solve()