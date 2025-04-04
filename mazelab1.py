import tkinter as tk
from tkinter import messagebox
from collections import deque


class MazePathFinder:
    def __init__(self, master):
        self.master = master
        self.master.title("Maze Pathfinding Visualization")

        # Maze configuration
        self.maze = [
            [1, 0, 1, 1, 1],
            [1, 1, 1, 0, 1],
            [0, 0, 0, 1, 1],
            [1, 1, 1, 1, 0],
            [1, 0, 0, 1, 1]
        ]
        self.start = (0, 0)
        self.end = (4, 4)

        # Create frames
        self.maze_frame = tk.Frame(master)
        self.maze_frame.pack(padx=10, pady=10)

        self.control_frame = tk.Frame(master)
        self.control_frame.pack(padx=10, pady=10)

        # Create maze grid buttons
        self.grid_buttons = []
        self.create_maze_grid()

        # Buttons for algorithms
        self.bfs_button = tk.Button(self.control_frame, text='BFS Pathfinding', command=self.run_bfs_step)
        self.bfs_button.pack(side=tk.LEFT, padx=5)

        self.dfs_button = tk.Button(self.control_frame, text='DFS Pathfinding', command=self.run_dfs_step)
        self.dfs_button.pack(side=tk.LEFT, padx=5)

        # Result label
        self.result_label = tk.Label(self.control_frame, text="", font=("Arial", 10))
        self.result_label.pack(side=tk.LEFT, padx=10)

        # Visualization variables
        self.current_path = []
        self.explored_nodes = set()

    def create_maze_grid(self):
        """Create visual representation of the maze."""
        for i in range(len(self.maze)):
            row_buttons = []
            for j in range(len(self.maze[0])):
                # Color codes
                bg_color = 'white' if self.maze[i][j] == 1 else 'black'

                # Create button for each cell
                btn = tk.Button(self.maze_frame, width=4, height=2, bg=bg_color,
                                state='normal' if self.maze[i][j] == 1 else 'disabled')
                btn.grid(row=i, column=j, padx=2, pady=2)
                row_buttons.append(btn)
            self.grid_buttons.append(row_buttons)

        # Mark start and end points
        self.grid_buttons[self.start[0]][self.start[1]].config(bg='green', text='Start')
        self.grid_buttons[self.end[0]][self.end[1]].config(bg='red', text='End')

    def reset_grid(self):
        """Reset grid to original state."""
        for i in range(len(self.maze)):
            for j in range(len(self.maze[0])):
                bg_color = 'white' if self.maze[i][j] == 1 else 'black'
                self.grid_buttons[i][j].config(bg=bg_color, text="")

        # Recolor start and end
        self.grid_buttons[self.start[0]][self.start[1]].config(bg='green', text='Start')
        self.grid_buttons[self.end[0]][self.end[1]].config(bg='red', text='End')

    def is_valid_move(self, x, y):
        """Check if move is valid."""
        return (0 <= x < len(self.maze) and
                0 <= y < len(self.maze[0]) and
                self.maze[x][y] == 1)

    def run_bfs_step(self):
        """Perform BFS with step-by-step visualization."""
        self.reset_grid()
        queue = deque([(self.start, [self.start])])
        self.explored_nodes = set([self.start])
        self.current_path = []

        def bfs_step():
            if not queue:
                messagebox.showinfo("BFS", "No path found!")
                return

            (x, y), path = queue.popleft()

            # Visualize explored node
            if (x, y) != self.start and (x, y) != self.end:
                self.grid_buttons[x][y].config(bg='yellow')

            if (x, y) == self.end:
                # Path found - visualize path
                self.visualize_path(path)
                return

            # Possible moves: right, down, left, up
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

            for dx, dy in directions:
                next_x, next_y = x + dx, y + dy

                if self.is_valid_move(next_x, next_y) and (next_x, next_y) not in self.explored_nodes:
                    queue.append(((next_x, next_y), path + [(next_x, next_y)]))
                    self.explored_nodes.add((next_x, next_y))

            if queue:
                self.master.after(500, bfs_step)
            else:
                messagebox.showinfo("BFS", "No path found!")

        # Start BFS visualization
        bfs_step()

    def run_dfs_step(self):
        """Perform DFS with step-by-step visualization."""
        self.reset_grid()
        stack = [(self.start, [self.start])]
        self.explored_nodes = set([self.start])
        self.current_path = []

        def dfs_step():
            if not stack:
                messagebox.showinfo("DFS", "No path found!")
                return

            (x, y), path = stack.pop()

            # Visualize explored node
            if (x, y) != self.start and (x, y) != self.end:
                self.grid_buttons[x][y].config(bg='purple')

            if (x, y) == self.end:
                # Path found - visualize path
                self.visualize_path(path)
                return

            # Possible moves: right, down, left, up
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

            for dx, dy in directions:
                next_x, next_y = x + dx, y + dy

                if self.is_valid_move(next_x, next_y) and (next_x, next_y) not in self.explored_nodes:
                    stack.append(((next_x, next_y), path + [(next_x, next_y)]))
                    self.explored_nodes.add((next_x, next_y))

            if stack:
                self.master.after(500, dfs_step)
            else:
                messagebox.showinfo("DFS", "No path found!")

        # Start DFS visualization
        dfs_step()

    def visualize_path(self, path):
        """Visualize the final path with color."""
        # Color the path blue
        for x, y in path[1:-1]:
            self.grid_buttons[x][y].config(bg='blue')

        # Show result
        result_text = f"Path Found! Length: {len(path)}, Explored Nodes: {len(self.explored_nodes)}"
        self.result_label.config(text=result_text)


def main():
    root = tk.Tk()
    root.title("Maze Pathfinding Visualization")
    app = MazePathFinder(root)
    root.mainloop()


if __name__ == '__main__':
    main()









