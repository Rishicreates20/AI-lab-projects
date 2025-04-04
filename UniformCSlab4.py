import tkinter as tk
from queue import PriorityQueue
from typing import Dict, List, Tuple
import random
import math
from collections import deque

class GraphNode:
    def __init__(self, x: int, y: int, node_id: str):
        self.x = x
        self.y = y
        self.id = node_id
        self.neighbors: Dict['GraphNode', float] = {}  # neighbor -> weight

    def add_neighbor(self, neighbor: 'GraphNode', weight: float):
        self.neighbors[neighbor] = weight

    def get_position(self) -> Tuple[int, int]:
        return self.x, self.y

class Graph:
    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}

    def add_node(self, node_id: str, x: int, y: int):
        self.nodes[node_id] = GraphNode(x, y, node_id)

    def add_edge(self, from_id: str, to_id: str, weight: float):
        if from_id in self.nodes and to_id in self.nodes:
            self.nodes[from_id].add_neighbor(self.nodes[to_id], weight)
            self.nodes[to_id].add_neighbor(self.nodes[from_id], weight)  # Undirected graph

class GraphSearchGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Graph Search Visualization")

        # Main Frame
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(expand=True, fill='both', padx=20, pady=20)

        # Canvas for graph visualization
        self.canvas_size = 600
        self.canvas = tk.Canvas(self.main_frame, width=self.canvas_size, height=self.canvas_size, bg='white')
        self.canvas.pack(side=tk.LEFT)

        # Control Panel
        self.control_panel = tk.Frame(self.main_frame)
        self.control_panel.pack(side=tk.LEFT, padx=20, fill='y')

        # Algorithm selection
        self.algo_var = tk.StringVar(value="UCS")
        tk.Label(self.control_panel, text="Algorithm:").pack(anchor='w')
        tk.Radiobutton(self.control_panel, text="Uniform Cost Search", variable=self.algo_var, value="UCS").pack(anchor='w')
        tk.Radiobutton(self.control_panel, text="Breadth-First Search", variable=self.algo_var, value="BFS").pack(anchor='w')

        # Buttons
        tk.Button(self.control_panel, text="Generate New Graph", command=self.generate_graph).pack(fill='x', pady=5)
        tk.Button(self.control_panel, text="Start Search", command=self.start_search).pack(fill='x', pady=5)
        tk.Button(self.control_panel, text="Reset", command=self.reset_visualization).pack(fill='x', pady=5)

        # Statistics
        self.stats_frame = tk.LabelFrame(self.control_panel, text="Statistics", padx=5, pady=5)
        self.stats_frame.pack(fill='x', pady=10)

        self.nodes_explored_var = tk.StringVar(value="Nodes explored: 0")
        self.path_cost_var = tk.StringVar(value="Path cost: 0")
        tk.Label(self.stats_frame, textvariable=self.nodes_explored_var).pack(anchor='w')
        tk.Label(self.stats_frame, textvariable=self.path_cost_var).pack(anchor='w')

        # Initialize Graph
        self.generate_graph()

    def generate_graph(self):
        self.graph = Graph()
        num_nodes = 10

        # Generate random nodes
        padding = 50
        for i in range(num_nodes):
            x = random.randint(padding, self.canvas_size - padding)
            y = random.randint(padding, self.canvas_size - padding)
            self.graph.add_node(str(i), x, y)

        # Generate random edges with weights
        node_ids = list(self.graph.nodes.keys())
        for i in range(num_nodes):
            for j in range(i + 1, num_nodes):
                if random.random() < 0.3:  # 30% chance of creating an edge
                    weight = round(math.dist(self.graph.nodes[node_ids[i]].get_position(),
                                             self.graph.nodes[node_ids[j]].get_position()), 2)
                    self.graph.add_edge(node_ids[i], node_ids[j], weight)

        self.start_node = node_ids[0]
        self.goal_node = node_ids[-1]

        self.draw_graph()

    def draw_graph(self):
        self.canvas.delete("all")

        # Draw edges
        for node in self.graph.nodes.values():
            for neighbor, weight in node.neighbors.items():
                self.canvas.create_line(node.x, node.y, neighbor.x, neighbor.y, fill="black", width=2)
                mid_x = (node.x + neighbor.x) // 2
                mid_y = (node.y + neighbor.y) // 2
                self.canvas.create_text(mid_x, mid_y, text=str(weight), fill="blue")

        # Draw nodes
        for node in self.graph.nodes.values():
            color = "red" if node.id == self.start_node else "green" if node.id == self.goal_node else "gray"
            self.canvas.create_oval(node.x - 10, node.y - 10, node.x + 10, node.y + 10, fill=color)
            self.canvas.create_text(node.x, node.y, text=node.id, fill="white")

    def start_search(self):
        algorithm = self.algo_var.get()
        if algorithm == "UCS":
            self.uniform_cost_search()
        elif algorithm == "BFS":
            self.breadth_first_search()

    def uniform_cost_search(self):
        start = self.graph.nodes[self.start_node]
        goal = self.graph.nodes[self.goal_node]
        visited = set()
        pq = PriorityQueue()
        pq.put((0, start, []))  # (cost, node, path)

        while not pq.empty():
            cost, current, path = pq.get()
            if current.id in visited:
                continue
            visited.add(current.id)
            path = path + [current]

            if current == goal:
                self.highlight_path(path, cost)
                return

            for neighbor, weight in current.neighbors.items():
                if neighbor.id not in visited:
                    pq.put((cost + weight, neighbor, path))

        self.nodes_explored_var.set(f"Nodes explored: {len(visited)}")
        self.path_cost_var.set("Path cost: No Path Found")

    def breadth_first_search(self):
        start = self.graph.nodes[self.start_node]
        goal = self.graph.nodes[self.goal_node]
        visited = set()
        queue = deque([(start, [])])  # (node, path)

        while queue:
            current, path = queue.popleft()
            if current.id in visited:
                continue
            visited.add(current.id)
            path = path + [current]

            if current == goal:
                self.highlight_path(path, len(path) - 1)
                return

            for neighbor in current.neighbors.keys():
                if neighbor.id not in visited:
                    queue.append((neighbor, path))

        self.nodes_explored_var.set(f"Nodes explored: {len(visited)}")
        self.path_cost_var.set("Path cost: No Path Found")

    def highlight_path(self, path, cost):
        for i in range(len(path) - 1):
            self.canvas.create_line(path[i].x, path[i].y, path[i + 1].x, path[i + 1].y, fill="blue", width=3)

        self.nodes_explored_var.set(f"Nodes explored: {len(path)}")
        self.path_cost_var.set(f"Path cost: {cost}")

    def reset_visualization(self):
        self.draw_graph()
        self.nodes_explored_var.set("Nodes explored: 0")
        self.path_cost_var.set("Path cost: 0")

if __name__ == "__main__":
    root = tk.Tk()
    app = GraphSearchGUI(root)
    root.mainloop()
