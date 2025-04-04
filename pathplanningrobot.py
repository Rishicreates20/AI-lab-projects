
import tkinter as tk
from tkinter import ttk
import math
import heapq
import time
import random
from collections import deque

class Node:
    def __init__(self, position, g_cost=float('inf'), h_cost=0):
        self.position = position
        self.g_cost = g_cost
        self.h_cost = h_cost
        self.f_cost = g_cost + h_cost
        self.parent = None

    def __lt__(self, other):
        return self.f_cost < other.f_cost

class PathPlanningVisualizer:
    def __init__(self, root, grid_size=10, cell_size=50):
        self.root = root
        self.grid_size = grid_size
        self.cell_size = cell_size
        self.current_algorithm = None
        self.open_set = []
        self.closed_set = set()
        self.path = []
        self.step_delay = 100
        self.metrics = {
            'path_length': 0,
            'path_cost': 0,
            'nodes_explored': 0,
            'execution_time': 0,
            'start_time': 0
        }

        self.root.title("Path Planning Visualization")
        self.grid = [[0 for _ in range(grid_size)] for _ in range(grid_size)]

        self.start = (1, 1)
        self.goal = (grid_size - 2, grid_size - 2)
        self.grid[self.start[0]][self.start[1]] = 'S'
        self.grid[self.goal[0]][self.goal[1]] = 'G'

        self.setup_ui()

    def setup_ui(self):
        control_frame = ttk.Frame(self.root)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        ttk.Label(control_frame, text="Algorithm:").pack(side=tk.LEFT)
        self.algo_var = tk.StringVar(value="A* (Manhattan)")
        algo_menu = ttk.OptionMenu(
            control_frame,
            self.algo_var,
            "A* (Manhattan)",
            "A* (Euclidean)",
            "BFS",
            "Uniform Cost"
        )
        algo_menu.pack(side=tk.LEFT, padx=5)

        ttk.Button(
            control_frame,
            text="Generate Random Obstacles",
            command=self.generate_obstacles
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            control_frame,
            text="Clear Path",
            command=self.clear_path
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            control_frame,
            text="Start Search",
            command=self.start_search
        ).pack(side=tk.LEFT, padx=5)

        ttk.Label(control_frame, text="Speed:").pack(side=tk.LEFT, padx=5)
        self.speed_scale = ttk.Scale(
            control_frame, from_=1, to=200,
            orient=tk.HORIZONTAL, length=100
        )
        self.speed_scale.set(100)
        self.speed_scale.pack(side=tk.LEFT)

        metrics_frame = ttk.LabelFrame(self.root, text="Algorithm Metrics")
        metrics_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        self.metrics_labels = {}
        metrics_grid = [
            ("Path Length:", "path_length"),
            ("Path Cost:", "path_cost"),
            ("Nodes Explored:", "nodes_explored"),
            ("Execution Time (ms):", "execution_time")
        ]
        for i, (label_text, metric_key) in enumerate(metrics_grid):
            ttk.Label(metrics_frame, text=label_text).grid(
                row=i, column=0, padx=5, pady=2, sticky='e'
            )
            label = ttk.Label(metrics_frame, text="0")
            label.grid(row=i, column=1, padx=5, pady=2, sticky='w')
            self.metrics_labels[metric_key] = label

        self.canvas = tk.Canvas(
            self.root,
            width=self.grid_size * self.cell_size,
            height=self.grid_size * self.cell_size
        )
        self.canvas.pack(padx=10, pady=10)

        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                # Determine the color of the cell based on its state
                if self.grid[i][j] == 1:
                    color = "black"
                elif (i, j) == self.start:
                    color = "green"
                elif (i, j) == self.goal:
                    color = "red"
                elif (i, j) in self.closed_set:
                    color = "light blue"
                elif any(node.position == (i, j) for node in self.open_set):
                    color = "yellow"
                elif (i, j) in self.path:
                    color = "blue"
                else:
                    color = "white"

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")

    def generate_obstacles(self):
        self.clear_path()
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if (i, j) != self.start and (i, j) != self.goal:
                    self.grid[i][j] = 1 if random.random() < 0.3 else 0
        self.draw_grid()

    def clear_path(self):
        self.open_set = []
        self.closed_set = set()
        self.path = []
        self.current_algorithm = None

        for key in self.metrics:
            self.metrics[key] = 0
        self.update_metrics()

        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if (i, j) != self.start and (i, j) != self.goal:
                    self.grid[i][j] = 0
        self.draw_grid()

    def manhattan_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def euclidean_distance(self, pos1, pos2):
        return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)

    def get_neighbours(self, pos, allow_diagonal=False):
        neighbors = []
        # Four-directional moves
        moves = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        if allow_diagonal:
            moves += [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dx, dy in moves:
            new_x, new_y = pos[0] + dx, pos[1] + dy
            if (0 <= new_x < self.grid_size and
                0 <= new_y < self.grid_size and
                self.grid[new_x][new_y] != 1):
                neighbors.append((new_x, new_y))
        return neighbors

    def reconstruct_path(self, current_node):
        path = []
        while current_node:
            path.append(current_node.position)
            current_node = current_node.parent
        return path[::-1]

    def update_metrics(self):
        for key, label in self.metrics_labels.items():
            label.config(text=str(self.metrics[key]))

    def calculate_path_cost(self, path):
        if not path:
            return 0
        cost = 0
        for i in range(len(path) - 1):
            dx = abs(path[i+1][0] - path[i][0])
            dy = abs(path[i+1][1] - path[i][1])
            cost += math.sqrt(dx**2 + dy**2)
        return cost

    def calculate_metrics(self, path, start_time):
        self.metrics['path_length'] = len(path) if path else 0
        self.metrics['path_cost'] = self.calculate_path_cost(path)
        self.metrics['nodes_explored'] = len(self.closed_set)
        self.metrics['execution_time'] = int((time.time() - start_time) * 1000)
        self.update_metrics()

    def a_star_search(self, heuristic):
        start_node = Node(self.start, 0, heuristic(self.start, self.goal))
        open_list = []
        heapq.heappush(open_list, start_node)
        self.open_set = [start_node]
        self.closed_set = set()

        while open_list:
            current_node = heapq.heappop(open_list)
            # Remove the current node from open_set used for drawing.
            self.open_set = [node for node in self.open_set if node.position != current_node.position]

            if current_node.position == self.goal:
                self.path = self.reconstruct_path(current_node)
                return self.path

            self.closed_set.add(current_node.position)

            for neighbor in self.get_neighbours(current_node.position):
                if neighbor in self.closed_set:
                    continue
                tentative_g = current_node.g_cost + self.euclidean_distance(current_node.position, neighbor)
                neighbor_node = Node(neighbor, tentative_g, heuristic(neighbor, self.goal))
                neighbor_node.parent = current_node
                heapq.heappush(open_list, neighbor_node)
                self.open_set.append(neighbor_node)

            # Update the canvas to animate the search
            self.draw_grid()
            self.root.update()
            time.sleep(self.speed_scale.get() / 1000.0)

        return []

    def bfs_search(self):
        start_node = Node(self.start, 0, 0)
        queue = deque([start_node])
        visited = set([self.start])
        self.open_set = [start_node]
        self.closed_set = set()

        while queue:
            current_node = queue.popleft()
            self.open_set = [node for node in self.open_set if node.position != current_node.position]

            if current_node.position == self.goal:
                self.path = self.reconstruct_path(current_node)
                return self.path

            self.closed_set.add(current_node.position)

            for neighbor in self.get_neighbours(current_node.position):
                if neighbor in visited:
                    continue
                visited.add(neighbor)
                neighbor_node = Node(neighbor, 0, 0)
                neighbor_node.parent = current_node
                queue.append(neighbor_node)
                self.open_set.append(neighbor_node)

            self.draw_grid()
            self.root.update()
            time.sleep(self.speed_scale.get() / 1000.0)

        return []

    def start_search(self):
        self.clear_path()  # Clear any old search results
        start_time = time.time()
        algo = self.algo_var.get()
        if "Manhattan" in algo:
            heuristic = self.manhattan_distance
            path = self.a_star_search(heuristic)
        elif "Euclidean" in algo:
            heuristic = self.euclidean_distance
            path = self.a_star_search(heuristic)
        elif "Uniform" in algo:
            heuristic = lambda pos, goal: 0
            path = self.a_star_search(heuristic)
        elif "BFS" in algo:
            path = self.bfs_search()
        else:
            # Default to A* using Manhattan
            heuristic = self.manhattan_distance
            path = self.a_star_search(heuristic)

        self.calculate_metrics(path, start_time)

    def on_canvas_click(self, event):
        # Optional: implement interactive features (e.g., set start/goal, place obstacles)
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = PathPlanningVisualizer(root, grid_size=20, cell_size=30)
    root.mainloop()
