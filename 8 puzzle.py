import tkinter as tk
from queue import PriorityQueue
from typing import List, Tuple, Optional
import random
import copy
import time


class PuzzleState:
    def __init__(self, board: List[List[int]], parent=None, move=""):
        self.board = board
        self.parent = parent
        self.move = move
        self.h = 0  # Heuristic value (misplaced tiles)
        self.g = 0  # Cost from start state
        self.f = 0  # Total cost (f = g + h)
        self.size = len(board)

    def __lt__(self, other):
        return self.f < other.f  # Compare total cost in A*

    def __eq__(self, other):
        return str(self.board) == str(other.board)

    def __hash__(self):
        return hash(str(self.board))

    def get_blank_pos(self) -> Tuple[int, int]:
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 0:
                    return (i, j)
        return (-1, -1)

    def get_possible_moves(self) -> List[Tuple[int, int]]:
        i, j = self.get_blank_pos()
        moves = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        for di, dj in directions:
            new_i, new_j = i + di, j + dj
            if 0 <= new_i < self.size and 0 <= new_j < self.size:
                moves.append((new_i, new_j))
        return moves

    def get_next_state(self, move_pos: Tuple[int, int]) -> 'PuzzleState':
        i, j = self.get_blank_pos()
        new_i, new_j = move_pos
        new_board = [row[:] for row in self.board]
        new_board[i][j], new_board[new_i][new_j] = new_board[new_i][new_j], new_board[i][j]
        return PuzzleState(new_board, self, "MOVE")


class PuzzleSolver:
    def __init__(self, initial_state: PuzzleState, goal_state: List[List[int]]):
        self.initial_state = initial_state
        self.goal_state = goal_state

    def heuristic(self, state: PuzzleState) -> int:
        return sum(
            1 for i in range(state.size) for j in range(state.size)
            if state.board[i][j] != 0 and state.board[i][j] != self.goal_state[i][j]
        )

    def solve(self) -> Optional[List[PuzzleState]]:
        open_set = PriorityQueue()
        open_set.put((0, self.initial_state))
        came_from = {}
        g_score = {str(self.initial_state.board): 0}
        f_score = {str(self.initial_state.board): self.heuristic(self.initial_state)}

        while not open_set.empty():
            _, current = open_set.get()
            if current.board == self.goal_state:
                return self.reconstruct_path(came_from, current)

            for move in current.get_possible_moves():
                neighbor = current.get_next_state(move)
                tentative_g_score = g_score[str(current.board)] + 1

                if str(neighbor.board) not in g_score or tentative_g_score < g_score[str(neighbor.board)]:
                    came_from[neighbor] = current
                    g_score[str(neighbor.board)] = tentative_g_score
                    f_score[str(neighbor.board)] = tentative_g_score + self.heuristic(neighbor)
                    open_set.put((f_score[str(neighbor.board)], neighbor))

        return None

    def reconstruct_path(self, came_from, current) -> List[PuzzleState]:
        path = []
        while current in came_from:
            path.append(current)
            current = came_from[current]
        path.reverse()
        return path


class PuzzleGUI:
    def __init__(self, root, initial_state: PuzzleState, goal_state: List[List[int]]):
        self.root = root
        self.state = initial_state
        self.goal_state = goal_state
        self.solver = PuzzleSolver(initial_state, goal_state)
        self.size = len(initial_state.board)
        self.buttons = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.create_ui()

    def create_ui(self):
        for i in range(self.size):
            for j in range(self.size):
                self.buttons[i][j] = tk.Button(self.root, text=str(self.state.board[i][j]),
                                               font=("Arial", 20), height=2, width=5,
                                               command=lambda x=i, y=j: self.move_tile(x, y))
                self.buttons[i][j].grid(row=i, column=j)

        self.shuffle_button = tk.Button(self.root, text="Shuffle", command=self.shuffle)
        self.shuffle_button.grid(row=self.size, column=0)

        self.start_button = tk.Button(self.root, text="Start", command=self.start_solving)
        self.start_button.grid(row=self.size, column=1)

        self.reset_button = tk.Button(self.root, text="Reset", command=self.reset)
        self.reset_button.grid(row=self.size, column=2)

        self.update_ui()

    def update_ui(self):
        for i in range(self.size):
            for j in range(self.size):
                value = self.state.board[i][j]
                self.buttons[i][j].config(text=str(value) if value != 0 else "", bg="lightgrey")
        self.root.update()

    def move_tile(self, i, j):
        blank_i, blank_j = self.state.get_blank_pos()
        if (i, j) in self.state.get_possible_moves():
            self.state = self.state.get_next_state((i, j))
            self.update_ui()

    def shuffle(self):
        flat_board = sum(self.state.board, [])
        random.shuffle(flat_board)
        new_board = [flat_board[i:i + self.size] for i in range(0, len(flat_board), self.size)]
        self.state = PuzzleState(new_board)
        self.update_ui()

    def start_solving(self):
        solution = self.solver.solve()
        if solution:
            for step in solution:
                self.state = step
                self.update_ui()
                time.sleep(0.5)

    def reset(self):
        self.state = PuzzleState([[1, 2, 3], [4, 5, 6], [7, 0, 8]])
        self.update_ui()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("8-Puzzle Solver")
    initial_board = [[1, 2, 3], [4, 5, 6], [7, 0, 8]]
    goal_board = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
    initial_state = PuzzleState(initial_board)
    gui = PuzzleGUI(root, initial_state, goal_board)
    root.mainloop()





