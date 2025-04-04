import tkinter as tk
from queue import PriorityQueue
import numpy as np
from typing import List, Tuple
import time


class TreasureHunt:
    def __init__(self, grid_size: int):
        self.grid_size = grid_size
        self.grid = np.random.randint(1, 10, (grid_size, grid_size))  # Random costs for cells

    def manhattan_distance(self, a: Tuple[int, int], b: Tuple[int, int]) -> int:
        """Calculate Manhattan distance between two points."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])


class TreasureHuntGUI:
    def __init__(self, root, grid_size: int, cell_size: int = 50):  # Reduced cell size
        self.root = root
        self.root.title("Treasure Hunt - Best First Search")
        self.grid_size = grid_size
        self.cell_size = cell_size

        # Main frame for canvas and info panel
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(expand=True, fill='both', padx=10, pady=10)

        # Canvas for the grid
        canvas_size = grid_size * cell_size
        self.canvas = tk.Canvas(self.main_frame, width=canvas_size, height=canvas_size, bg="white")
        self.canvas.pack(side=tk.LEFT)

        # Info panel
        self.info_panel = tk.Frame(self.main_frame, bg="white")
        self.info_panel.pack(side=tk.LEFT, padx=10, fill='y')

        # Control panel
        self.control_panel = tk.Frame(self.info_panel)
        self.control_panel.pack(fill='x', pady=5)

        # Start button
        self.start_button = tk.Button(self.control_panel, text="Start Hunt", command=self.start_hunt)
        self.start_button.pack(fill='x', pady=1)

        # Reset button
        self.reset_button = tk.Button(self.control_panel, text="Reset", command=self.initialize_game)
        self.reset_button.pack(fill='x', pady=1)

        # Speed control
        speed_frame = tk.Frame(self.control_panel)
        speed_frame.pack(fill='x')
        tk.Label(speed_frame, text="Speed").pack(side=tk.LEFT)
        self.speed_var = tk.StringVar(value="Normal")
        self.speed_menu = tk.OptionMenu(speed_frame, self.speed_var, "Slow", "Normal", "Fast")
        self.speed_menu.pack(side=tk.LEFT, padx=5)

        # Node selection
        node_frame = tk.Frame(self.control_panel)
        node_frame.pack(fill='x', pady=5)

        tk.Label(node_frame, text="Start Node:").pack(side=tk.LEFT)
        self.start_var = tk.StringVar(value="(0, 0)")
        self.start_menu = tk.OptionMenu(node_frame, self.start_var, *self.generate_node_options())
        self.start_menu.pack(side=tk.LEFT, padx=5)

        tk.Label(node_frame, text="End Node:").pack(side=tk.LEFT)
        self.end_var = tk.StringVar(value=f"({grid_size-1}, {grid_size-1})")
        self.end_menu = tk.OptionMenu(node_frame, self.end_var, *self.generate_node_options())
        self.end_menu.pack(side=tk.LEFT, padx=5)

        # Statistics
        stats_frame = tk.Frame(self.info_panel, bg="white")
        stats_frame.pack(fill='x', pady=5)

        self.nodes_explored_var = tk.StringVar(value="Nodes explored: 0")
        tk.Label(stats_frame, textvariable=self.nodes_explored_var).pack(anchor='w')

        self.path_length_var = tk.StringVar(value="Path length: 0")
        tk.Label(stats_frame, textvariable=self.path_length_var).pack(anchor='w')

        # Legend
        legend_frame = tk.Frame(self.info_panel, bg="white")
        legend_frame.pack(fill='x', pady=5)

        legend_items = [
            ("Start", "Green"),
            ("Target", "Gold"),
            ("Current Node", "Yellow"),
            ("Path", "Red"),
            ("Explored", "Pink"),
            ("Frontier", "Light Green")
        ]

        for text, color in legend_items:
            frame = tk.Frame(legend_frame)
            frame.pack(fill='x', padx=1)
            tk.Canvas(frame, width=20, height=20, bg=color).pack(side=tk.LEFT, padx=5)
            tk.Label(frame, text=text).pack(side=tk.LEFT)

        self.initialize_game()

    def generate_node_options(self):
        """Generate a list of node options for the menu."""
        return [f"({i}, {j})" for i in range(self.grid_size) for j in range(self.grid_size)]

    def get_animation_delay(self):
        speeds = {"Slow": 1000, "Normal": 500, "Fast": 100}
        return speeds[self.speed_var.get()] / 1000  # Convert to seconds

    def draw_grid(self):
        """Draw the initial grid with heuristic values."""
        self.canvas.delete("all")
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                self.draw_cell((i, j), "white", str(self.hunt.grid[i, j]))

    def draw_cell(self, pos: Tuple[int, int], color: str, text: str = "", show_heuristic: bool = True):
        """Draw a colored cell with heuristic value and optional text."""
        x1 = pos[1] * self.cell_size
        y1 = pos[0] * self.cell_size
        x2 = x1 + self.cell_size
        y2 = y1 + self.cell_size

        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray", tags="cell")
        if text:
            self.canvas.create_text(x1 + self.cell_size / 2, y1 + self.cell_size / 2, text=text, font=("Arial", 10, "bold"))

    def initialize_game(self):
        """Set up the initial game state with start and goal positions."""
        self.start_pos = eval(self.start_var.get())  # Start at top-left corner
        self.target_pos = eval(self.end_var.get())  # Goal at bottom-right corner
        self.hunt = TreasureHunt(self.grid_size)

        self.draw_grid()

        # Highlight the start and goal positions
        self.draw_cell(self.start_pos, "green", "S")
        self.draw_cell(self.target_pos, "gold", "G")

        # Reset statistics
        self.nodes_explored_var.set("Nodes explored: 0")
        self.path_length_var.set("Path length: 0")

    def start_hunt(self):
        """Run Best-First Search to find the treasure."""
        frontier = PriorityQueue()
        frontier.put((0, self.start_pos))
        came_from = {}
        nodes_explored = 0
        came_from[self.start_pos] = None

        while not frontier.empty():
            _, current = frontier.get()

            # Highlight the current node being explored
            self.draw_cell(current, "yellow")
            self.root.update()
            time.sleep(self.get_animation_delay())

            if current == self.target_pos:  # If goal is reached
                path = []
                while current:
                    path.append(current)
                    current = came_from.get(current)
                path.reverse()

                # Draw the path
                for pos in path:
                    self.draw_cell(pos, "red")
                    self.root.update()
                    time.sleep(self.get_animation_delay())

                self.path_length_var.set(f"Path length: {len(path)}")
                return

            nodes_explored += 1
            self.nodes_explored_var.set(f"Nodes explored: {nodes_explored}")

            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # Move in 4 directions
                neighbor = (current[0] + dx, current[1] + dy)
                if 0 <= neighbor[0] < self.grid_size and 0 <= neighbor[1] < self.grid_size:
                    priority = self.hunt.manhattan_distance(neighbor, self.target_pos)
                    if neighbor not in came_from:
                        frontier.put((priority, neighbor))
                        came_from[neighbor] = current

            # Mark explored nodes
            if current != self.start_pos and current != self.target_pos:
                self.draw_cell(current, "pink")


if __name__ == "__main__":
    root = tk.Tk()
    app = TreasureHuntGUI(root, grid_size=10)
    root.mainloop()



