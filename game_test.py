import arcade
from enum import Enum
import json
from collections import namedtuple
from tree import Node, NodeValue
from grid_aux import load_grid, GridData, GridElement, Coordinate
import time
import logging
from datetime import datetime
from collections import deque
import heapq
import glob
import math

# Define directions
class Direction(Enum):    
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)

MoveResult = namedtuple('MoveResult', ['moved', 'new_position', 'boxes_positions'])

class TreeData:
    def __init__(self, frontier, expanded_node_count, frontier_node_count):
        self.expanded_node_count = expanded_node_count
        self.frontier_node_count = frontier_node_count
        self.frontier = frontier
        self.visited = set()

    def __str__(self) -> str:
        return f"Expanded nodes: {self.expanded_node_count}, Frontier nodes: {self.frontier_node_count}"

    def __repr__(self) -> str:
        return self.__str__()
    

# This sets the WIDTH and HEIGHT of each grid location
WIDTH = 30
HEIGHT = 30

# This sets the margin between each cell
# and on the edges of the screen.
MARGIN = 5

HORIZONTAL_GRIDS_COUNT = 3

MAX_HEIGHT = 1000
MAX_WIDTH = 1600

# Do the math to figure out our screen dimensions
SCREEN_TITLE = "Sokoban"

with open('config.json') as f:
    config = json.load(f)

allowed_algorithms = ['bfs', 'dfs', 'a_star', 'greedy']
if config['algorithm'] not in allowed_algorithms:
    raise ValueError(f"Invalid algorithm: {config['algorithm']}. Allowed options are {allowed_algorithms}.")

sorting_options = {
    'bfs': None,
    'a_star': lambda x: (x.value.heuristic + x.value.depth/5, x.value.heuristic), # TODO preguntar, demasiado peso al depth? Se puede cambiar?
    'greedy': lambda x: x.value.heuristic
}

class Sokoban(arcade.Window):
    def __init__(self, title, grid_datas: list, routes=[], grid_algorithms: list = [], close_on_finish=False):
        global WIDTH, HEIGHT, MARGIN

        self.time_since_last_move = 0

        width = 0
        height = 0
        self.paused = False
        self.close_on_finish = close_on_finish

        if grid_datas and len(grid_datas) == 0:
            raise ValueError("No grids to show")
        for grid_data in grid_datas:
            if len(grid_data.grid) == 0:
                raise ValueError("Initial grid cannot be empty")
        self.grids = grid_datas

        self.routes = routes
        self.max_grid_width = max([len(grid.grid[0]) for grid in grid_datas])
        self.max_grid_height = max([len(grid.grid) for grid in grid_datas])
        self.grid_algorithms = grid_algorithms
        for grid_data in grid_datas:
            self.grid_row_count = math.ceil(len(grid_datas)/HORIZONTAL_GRIDS_COUNT)

        self.steps = [0 for _ in grid_datas]

        horizontal_grids = min(HORIZONTAL_GRIDS_COUNT, len(grid_datas))
        width = (WIDTH + MARGIN) * self.max_grid_width * horizontal_grids + MARGIN + WIDTH * (horizontal_grids - 1) + 5*WIDTH
        height = (WIDTH + MARGIN) * self.max_grid_height * self.grid_row_count + MARGIN + HEIGHT * (self.grid_row_count)

        while width > MAX_WIDTH or height > MAX_HEIGHT:
            relation = min(MAX_WIDTH / width, MAX_HEIGHT / height)
            WIDTH = int(WIDTH * relation)
            HEIGHT = int(HEIGHT * relation)
            MARGIN = int(MARGIN * relation)
            width = (WIDTH + MARGIN) * self.max_grid_width * horizontal_grids + MARGIN + WIDTH * (horizontal_grids - 1) + 5*WIDTH
            height = (WIDTH + MARGIN) * self.max_grid_height * self.grid_row_count + MARGIN + HEIGHT * (self.grid_row_count)
        
        super().__init__(width, height, title)

        self.step = 0

        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        # This command has to happen before we start drawing
        self.clear()

        # Draw the grid
        for i, grid in enumerate(self.grids):   

            if (i % HORIZONTAL_GRIDS_COUNT) == 0:
                grid_height = (MARGIN + HEIGHT) * self.max_grid_height
                text_y = self.height - (MARGIN + HEIGHT) * (self.max_grid_height+1) * ((i // HORIZONTAL_GRIDS_COUNT)+1) + grid_height / 2
                text_x = WIDTH
                arcade.draw_text(self.grid_algorithms[i], text_x, text_y, arcade.color.YELLOW, 14)

            for row in range(len(grid.grid)):                    
                for column in range(len(grid.grid[0])):
                    # Figure out what color to draw the box
                    if grid.player_position == Coordinate(row, column):
                        color = arcade.color.RED
                        shape = arcade.draw_circle_filled
                    elif grid.boxes_positions.count(Coordinate(row, column)) > 0:
                        color = arcade.color.BLUE
                        shape = arcade.draw_rectangle_filled
                    elif grid.grid[row][column] == GridElement.OBJECTIVE:
                        color = arcade.color.GREEN
                        shape = arcade.draw_rectangle_filled
                    elif grid.grid[row][column] == GridElement.FILLED:
                        color = arcade.color.WHITE
                        shape = arcade.draw_rectangle_filled
                    else:
                        color = arcade.color.BLACK
                        shape = arcade.draw_rectangle_filled

                    grid_x_offset = (MARGIN + WIDTH) * self.max_grid_width * (i % HORIZONTAL_GRIDS_COUNT) + WIDTH * (i % HORIZONTAL_GRIDS_COUNT)
                    grid_y_offset = (MARGIN + HEIGHT) * self.max_grid_height * (i // HORIZONTAL_GRIDS_COUNT) + HEIGHT * (i // HORIZONTAL_GRIDS_COUNT)

                    # Do the math to figure out where the box is
                    x = (MARGIN + WIDTH) * column + MARGIN + WIDTH // 2 + grid_x_offset + 5*WIDTH
                    y = self.height - ((MARGIN + HEIGHT) * row + MARGIN + HEIGHT // 2 + grid_y_offset)
                    height_diff = self.max_grid_height - len(grid.grid)
                    y -= height_diff * (WIDTH + MARGIN) / 2
                    width_diff = self.max_grid_width - len(grid.grid[0])
                    x += width_diff * (WIDTH + MARGIN) / 2

                    if shape == arcade.draw_circle_filled:
                        shape(x, y, WIDTH // 2, color)  
                    else:
                        shape(x, y, WIDTH, HEIGHT, color)

    def update(self, delta_time):
        if self.paused:
            return
        
        # Llamar al algoritmo aca
        self.time_since_last_move += delta_time
    
        move_delta = config["replay"]["speed"] if config["replay"]["enabled"] else 0.01

        if self.time_since_last_move >= move_delta:

            finished_count = 0
            for i, grid_data in enumerate(self.grids):
                if self.steps[i] < len(self.routes[i]):
                    result = move_player(Direction[self.routes[i][self.steps[i]]], grid_data)
                    grid_data.player_position = result.new_position
                    grid_data.boxes_positions = result.boxes_positions
                    self.steps[i] += 1
                else:
                    finished_count += 1
            if finished_count == len(self.grids):
                self.paused = True
                if self.close_on_finish:
                    arcade.close_window()
                return

            self.time_since_last_move = 0

        return super().update(delta_time)

# Check if the player can move into a cell
def can_move_into_cell(direction, grid_data: GridData, current_position: Coordinate):
    attempted_position = current_position.move(direction.value)
    row = attempted_position.row
    column = attempted_position.column
    if row < 0 or column < 0 or row >= len(grid_data.grid) or column >= len(grid_data.grid[0]):
        return False
    return grid_data.grid[row][column] in {GridElement.EMPTY, GridElement.OBJECTIVE} and grid_data.boxes_positions.count(attempted_position) == 0

# Move the player. Checks if the player can move into a cell and if there is a box in the cell, if the box can be moved
# Returns a MoveResult with the new position and the new boxes positions, and a boolean indicating if the player moved
def move_player(direction: Direction, grid_data: GridData): 
    new_position = grid_data.player_position.move(direction.value)
    if can_move_into_cell(direction, grid_data, grid_data.player_position):
        return MoveResult(True, new_position, grid_data.boxes_positions)
    elif grid_data.boxes_positions.count(new_position) > 0:
        if can_move_into_cell(direction, grid_data, new_position):
            box_new_position = new_position.move(direction.value)
            aux = grid_data.boxes_positions.copy()
            aux.remove(new_position)
            aux.append(box_new_position)
            return MoveResult(True, new_position, aux)
    return MoveResult(False, grid_data.player_position, grid_data.boxes_positions)

# Explore all possible moves from a given node
def explore_node(node, grid_data):
    for direction in Direction:        
        result = move_player(direction, grid_data)
        if result.moved:
            heuristic = calculate_heuristic(grid_data.grid, grid_data.objective_positions, result.boxes_positions, result.new_position)
            node.add_child(Node(NodeValue(result.new_position, result.boxes_positions, direction, heuristic, node.value.depth + 1)))
    return node

def execute_step(grid_data: GridData, data: TreeData):
    step_result = algorithm_step(grid_data, data)
    new_position = step_result[0]
    grid_data.player_position = new_position.value.player_position
    grid_data.boxes_positions = new_position.value.boxes_positions

    if step_result[1]:
        message = f"Grid: {grid_data.name}\nSolution found with '{config['algorithm']}' algorithm and heuristic {config['heuristic']}\n{data}\nRoute depth: {new_position.value.depth}"
        print(message)
        logging.info(message)
        route = []
        while new_position.parent:
            route.append(new_position.value.direction.name)
            new_position = new_position.parent
        logging.info(route[::-1])

        filename = f"replay_{grid_data.name}_{config['algorithm']}.json"
        json_data = {
            "grid": grid_data.original(new_position.value.player_position, new_position.value.boxes_positions),
            "name": grid_data.name,
            "route": route[::-1],
            "algorithm": config['algorithm']
        }
        with open(filename, 'w') as f:
            json.dump(json_data, f)
        return True
    
    if data.frontier == []:
        print("No solution found")
        return True

    return False
    
def algorithm_step(grid_data: GridData, data: TreeData):
    if config['algorithm'] == 'dfs':
        node = data.frontier.pop()
    elif config['algorithm'] == 'bfs':
        node = data.frontier.popleft()
    else:
        _, _, node = heapq.heappop(data.frontier)

    if is_solution(grid_data.grid, node.value.boxes_positions):
        return node, True
    
    aux_grid_data = grid_data.copy()
    aux_grid_data.player_position = node.value.player_position
    aux_grid_data.boxes_positions = node.value.boxes_positions
    
    explore_node(node, aux_grid_data)
    data.expanded_node_count += 1
    data.frontier_node_count -= 1
    for child in node.children:
        if child not in data.visited and child.value.heuristic < float('inf'):  # Check if state has been visited ans is viable
            if config['algorithm'] == 'dfs':
                data.frontier.append(child)
            elif config['algorithm'] == 'bfs':
                data.frontier.append(child)
            else:
                heapq.heappush(data.frontier, (sorting_options[config['algorithm']](child), data.expanded_node_count, child))
            data.frontier_node_count += 1                
            data.visited.add(child)  # Add state to visited set

    return node, False
    
# Decide if the game has been solved
def is_solution(grid, boxes_positions):
    return all([grid[coordinate.row][coordinate.column] == GridElement.OBJECTIVE for coordinate in boxes_positions])


def calculate_heuristic(grid, objective_positions, boxes_positions, player_position):
    if config['heuristic'] == 1:
        return calculate_first_heuristic(grid, objective_positions, boxes_positions, player_position)
    elif config['heuristic'] == 2:
        return calculate_second_heuristic(grid, objective_positions, boxes_positions, player_position)
    elif config['heuristic'] == 3:
        return calculate_third_heuristic(grid, objective_positions, boxes_positions, player_position)
    else:
        raise ValueError(f"Invalid heuristic: {config['heuristic']}. Allowed options are 1, 2 and 3.")
    
def is_box_in_corner(grid, box):
    if grid[box.row][box.column] == GridElement.OBJECTIVE:
            return False
    filled_sides = {direction: False for direction in Direction}
    for direction in Direction:
        if grid[box.row + direction.value[0]][box.column + direction.value[1]] == GridElement.FILLED:
            filled_sides[direction] = True
    return (filled_sides[Direction.UP] or filled_sides[Direction.DOWN]) and (filled_sides[Direction.RIGHT] or filled_sides[Direction.LEFT])

def calculate_first_heuristic(grid, objective_positions, boxes_positions, player_position):
    base_value = sum([min([abs(obj.row - box.row) + abs(obj.column - box.column) for obj in objective_positions]) for box in boxes_positions])
    for box in boxes_positions:
        if is_box_in_corner(grid, box):
            base_value = float('inf')
            break
    return base_value

def calculate_second_heuristic(grid, objective_positions, boxes_positions, player_position):
    base_value = 0
    objectives_assigned = [False for _ in objective_positions]

    for box in boxes_positions:
        if is_box_in_corner(grid, box):
            base_value = float('inf')
            break

        min_distance = float('inf')
        min_index = -1
        for i, obj in enumerate(objective_positions):
            if objectives_assigned[i]:
                continue
            distance = abs(obj.row - box.row) + abs(obj.column - box.column)
            if distance < min_distance:
                min_distance = distance
                min_index = i
        if min_index != -1:
            objectives_assigned[min_index] = True
        base_value += min_distance
    return base_value

# calculate the distance from each box to the farthest objective
def calculate_third_heuristic(grid, objective_positions, boxes_positions, player_position):
    base_value = 0
    for box in boxes_positions:
        if is_box_in_corner(grid, box):
            base_value = float('inf')
            break

        max_distance = float('-inf')
        for obj in objective_positions:
            distance = abs(obj.row - box.row) + abs(obj.column - box.column)
            if distance > max_distance:
                max_distance = distance
        base_value += max_distance
    return base_value

def initialize_tree(grid_data: GridData):
    heuristic = calculate_heuristic(grid_data.grid, grid_data.objective_positions, grid_data.boxes_positions, grid_data.player_position)
    frontier = []
    first_node = Node(NodeValue(grid_data.player_position, grid_data.boxes_positions, None, heuristic, 0))
    if config['algorithm'] == 'dfs':
        frontier.append(first_node)
    elif config['algorithm'] == 'bfs':
        frontier = deque([first_node])
    else:
        heapq.heappush(frontier, (sorting_options[config['algorithm']](first_node), 0, first_node))

    explore_data = TreeData(frontier, 0, 1)
    return explore_data

def main():

    if config["replay"]["enabled"]:
        grid_datas = []
        routes = []
        grid_algorithms = []
        filenames = []
        for path in config["replay"]["paths"]:
            filenames.extend(glob.glob(path))
        for filename in filenames:
            with open(filename) as f:
                grid = json.load(f)
                grid_datas.append(load_grid(grid))
                routes.append(grid["route"])
                grid_algorithms.append(grid["algorithm"])
        
        combined = list(zip(grid_algorithms, grid_datas, routes))
        combined.sort()
        grid_algorithms, grid_datas, routes = zip(*combined)

        if config["replay"]["sequential"]:
            for i, grid in enumerate(grid_datas):
                screen_title = f"Sokoban - {grid_algorithms[i]}"
                Sokoban(screen_title, [grid], [routes[i]], [grid_algorithms[i]], i != len(grid_datas) - 1)
                arcade.run()
        else:
            screen_title = f"Sokoban"
            Sokoban(screen_title, grid_datas, routes, grid_algorithms)
            arcade.run()
    else:
        log_filename = f"log_{config['algorithm']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        logging.basicConfig(filename=log_filename, level=logging.INFO, filemode='w', format='%(message)s')
        with open('grid.json') as f:
            grids = json.load(f)['active']
            for grid in grids:
                start_time = time.process_time()
                last_time = start_time
                grid_data = load_grid(grid)
                explore_data = initialize_tree(grid_data)
                while not execute_step(grid_data, explore_data):
                    current_time = time.process_time()
                    if (current_time - last_time) > config["print_delta_time"]:
                        print(f"Time: {current_time - start_time:.2f}")
                        last_time = current_time
                    pass
                print(f"Time: {time.process_time() - start_time:.2f}")
                logging.info(f"Time: {time.process_time() - start_time:.2f}")
                print("---------------------------------------------------")
                logging.info("---------------------------------------------------")


if __name__ == "__main__":
    main()