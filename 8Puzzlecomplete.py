import heapq
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

# Goal state of the 8-puzzle
GOAL_STATE = (1, 2, 3, 4, 5, 6, 7, 8, 0)
GOAL_TILES = {tile: idx for idx, tile in enumerate(GOAL_STATE)}


def h1(state):
    """Heuristic 1: Number of misplaced tiles excluding the blank."""
    return sum(1 for i in range(9) if state[i] != GOAL_STATE[i] and state[i] != 0)


def h2(state):
    """Heuristic 2: Sum of Manhattan distances of all tiles from their goal positions."""
    sum_distance = 0
    for idx in range(9):
        tile = state[idx]
        if tile == 0:
            continue
        goal_idx = GOAL_TILES[tile]
        current_row, current_col = divmod(idx, 3)
        goal_row, goal_col = divmod(goal_idx, 3)
        sum_distance += abs(current_row - goal_row) + abs(current_col - goal_col)
    return sum_distance


def a_star(initial_state, heuristic_func):
    """Perform A* search using the specified heuristic function."""
    open_list = []
    heapq.heappush(open_list, (0, 0, 0, initial_state, None))  # (f, h, g, state, parent)
    closed_set = set()
    nodes_explored = 0

    while open_list:
        current_f, current_h, current_g, current_state, parent = heapq.heappop(open_list)
        nodes_explored += 1

        if current_state == GOAL_STATE:
            # Reconstruct the path
            path = []
            node = (current_state, parent)
            while node is not None:
                path.append(node[0])
                node = node[1]
            path.reverse()
            return path, nodes_explored, current_g

        if current_state in closed_set:
            continue
        closed_set.add(current_state)

        # Generate all possible next states
        blank_pos = current_state.index(0)
        row, col = divmod(blank_pos, 3)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 3 and 0 <= new_col < 3:
                new_blank_pos = new_row * 3 + new_col
                state_list = list(current_state)
                # Swap blank with the new position
                state_list[blank_pos], state_list[new_blank_pos] = state_list[new_blank_pos], state_list[blank_pos]
                new_state = tuple(state_list)

                if new_state in closed_set:
                    continue

                new_g = current_g + 1
                new_h = heuristic_func(new_state)
                new_f = new_g + new_h

                heapq.heappush(open_list, (new_f, new_h, new_g, new_state, (current_state, parent)))

    # If no solution found
    return None, nodes_explored, 0


def plot_puzzle(state, ax):
    """Plot the 8-puzzle state."""
    ax.clear()
    ax.set_xticks([])
    ax.set_yticks([])
    for i in range(3):
        for j in range(3):
            tile = state[i * 3 + j]
            if tile != 0:
                ax.text(j, 2 - i, str(tile), fontsize=20, ha='center', va='center')
            ax.add_patch(plt.Rectangle((j - 0.5, 2 - i - 0.5), 1, 1, fill=False, edgecolor='black'))
    ax.set_xlim(-0.5, 2.5)
    ax.set_ylim(-0.5, 2.5)
    ax.set_aspect('equal')


def animate_solution(path):
    """Animate the solution path."""
    fig, ax = plt.subplots()
    frames = []

    for state in path:
        frames.append(state)

    def update(frame):
        plot_puzzle(frame, ax)

    ani = FuncAnimation(fig, update, frames=frames, interval=500, repeat=False)
    plt.show()


def main():
    """Test A* with different initial states and heuristics."""
    initial_states = [
        (1, 2, 3, 4, 5, 6, 7, 8, 0),  # Goal state
        (1, 2, 3, 4, 5, 6, 7, 0, 8),  # One move away
        (1, 2, 3, 4, 5, 6, 0, 7, 8),  # Two moves away
        (1, 2, 3, 0, 4, 6, 7, 5, 8),  # Requires more steps
        (8, 1, 3, 4, 0, 2, 7, 6, 5)   # Complex case (may take longer)
    ]

    for idx, initial_state in enumerate(initial_states):
        print(f"Testing initial state {idx + 1}: {initial_state}")
        for heuristic_name, heuristic_func in [('H1', h1), ('H2', h2)]:
            print(f"Using heuristic {heuristic_name}:")
            path, nodes_explored, depth = a_star(initial_state, heuristic_func)
            if path:
                print(f"Solution depth: {depth}")
                print(f"Nodes explored: {nodes_explored}")
                animate_solution(path)  # Animate the solution
            else:
                print("No solution found")
            print("------")
        print("======================")


if __name__ == "__main__":
    main()