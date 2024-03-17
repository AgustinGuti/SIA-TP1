import arcade
from enum import Enum
from collections import namedtuple
from tree import Node, NodeValue
from grid_aux import load_grid_from_file, GridData, GridElement, Coordinate

# Define directions
class Direction(Enum):    
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)

MoveResult = namedtuple('MoveResult', ['moved', 'new_position', 'boxes_positions'])

class TreeData:
    def __init__(self, queue, expanded_node_count, frontier_node_count):
        self.expanded_node_count = expanded_node_count
        self.frontier_node_count = frontier_node_count
        self.queue = queue
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

# Do the math to figure out our screen dimensions
SCREEN_TITLE = "Example Game"

class Sokoban(arcade.Window):
    def __init__(self, title, grid_data: GridData, showcase=False):
        if len(grid_data.grid) == 0:
            raise ValueError("Initial grid cannot be empty")
        
        self.row_count = len(grid_data.grid)
        self.column_count = len(grid_data.grid[0])
        
        width = (WIDTH + MARGIN) * self.column_count + MARGIN
        height = (WIDTH + MARGIN) * self.row_count + MARGIN

        self.paused = False

        super().__init__(width, height, title)

        # Create a 2 dimensional array. A two-dimensional
        # array is simply a list of lists.
        self.grid_data = grid_data
        self.time_since_last_move = 0
        self.showcase = showcase

        self.explore_data = TreeData([Node(NodeValue(grid_data.player_position, grid_data.boxes_positions, None))], 0, 1)

        self.step = 0


        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        # This command has to happen before we start drawing
        self.clear()

        # Draw the grid
        for row in range(self.row_count):
            for column in range(self.column_count):
                # Figure out what color to draw the box
        
                if self.grid_data.player_position == Coordinate(row, column):
                    color = arcade.color.RED
                    shape = arcade.draw_circle_filled
                elif self.grid_data.boxes_positions.count(Coordinate(row, column)) > 0:
                    color = arcade.color.BLUE
                    shape = arcade.draw_rectangle_filled
                elif self.grid_data.grid[row][column] == GridElement.OBJECTIVE:
                    color = arcade.color.GREEN
                    shape = arcade.draw_rectangle_filled
                elif self.grid_data.grid[row][column] == GridElement.FILLED:
                    color = arcade.color.WHITE
                    shape = arcade.draw_rectangle_filled
                else:
                    color = arcade.color.BLACK
                    shape = arcade.draw_rectangle_filled

                # Do the math to figure out where the box is
                x = (MARGIN + WIDTH) * column + MARGIN + WIDTH // 2
                y = self.height - ((MARGIN + HEIGHT) * row + MARGIN + HEIGHT // 2)
                
                if shape == arcade.draw_circle_filled:
                    shape(x, y, WIDTH // 2, color)  # Draw a circle if the shape is a circle
                else:
                    shape(x, y, WIDTH, HEIGHT, color)  # Draw a rectangle otherwise        

    def update(self, delta_time):
        if self.paused:
            return
        
        # Llamar al algoritmo aca
        self.time_since_last_move += delta_time
    
        if self.time_since_last_move >= 0.01:  # half a second has passed  

            if not self.showcase:
                step_result = greedy_step(self.grid_data, self.explore_data)
                new_position = step_result[0]
                self.grid_data.player_position = new_position.value.player_position
                self.grid_data.boxes_positions = new_position.value.boxes_positions

                if step_result[1]:
                    print("Solution found")
                    print(self.explore_data)
                    route = []
                    while new_position.parent:
                        route.append(new_position.value.direction.name)
                        new_position = new_position.parent
                    print(route[::-1])
                    self.paused = True
                    return
                
                if self.explore_data.queue == []:
                    print("No solution found")
                    self.paused = True
                    return
            else:
                # route for base grid.json
                route = ['LEFT', 'RIGHT', 'RIGHT', 'LEFT', 'UP', 'UP', 'LEFT', 'LEFT', 'DOWN', 'LEFT', 'DOWN', 'DOWN', 'RIGHT', 'UP', 'UP', 'UP', 'UP', 'DOWN', 'DOWN', 'DOWN', 'LEFT', 'LEFT', 'LEFT', 'LEFT', 'UP', 'UP', 'RIGHT', 'UP', 'RIGHT', 'UP', 'RIGHT', 'RIGHT', 'RIGHT', 'LEFT', 'DOWN', 'DOWN', 'RIGHT', 'RIGHT', 'UP', 'UP', 'UP', 'DOWN', 'DOWN', 'DOWN', 'RIGHT', 'RIGHT', 'DOWN', 'RIGHT', 'DOWN', 'DOWN', 'LEFT', 'UP', 'UP', 'UP', 'UP', 'DOWN', 'DOWN', 'DOWN', 'RIGHT', 'RIGHT', 'RIGHT', 'RIGHT', 'UP', 'UP', 'LEFT', 'UP', 'LEFT', 'UP', 'LEFT', 'LEFT', 'LEFT', 'RIGHT', 'DOWN', 'DOWN', 'LEFT', 'LEFT', 'UP', 'UP']

                if self.step < len(route):
                    result = move_player(Direction[route[self.step]], self.grid_data)
                    self.grid_data.player_position = result.new_position
                    self.grid_data.boxes_positions = result.boxes_positions
                    self.step += 1

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
            heuristic = calculate_heuristic(objective_positions=grid_data.objective_positions, boxes_positions=result.boxes_positions)
            node.add_child(Node(NodeValue(result.new_position, result.boxes_positions, direction, heuristic)))
    return node
    
# Perform a step in the BFS algorithm
def bfs_step(grid_data: GridData, data: TreeData):
    node = data.queue.pop(0)
    if is_solution(grid_data.grid, node.value.boxes_positions, node.value.player_position):
        return node, True
    aux_grid_data = grid_data.copy()
    aux_grid_data.player_position = node.value.player_position
    aux_grid_data.boxes_positions = node.value.boxes_positions
    explore_node(node, aux_grid_data)
    data.expanded_node_count += 1
    data.frontier_node_count -= 1
    for child in node.children:
        # TODO hash
        child_state = (child.value.player_position, tuple(sorted(child.value.boxes_positions)))
        if child_state not in data.visited:  # Check if state has been visited
            data.queue.append(child)
            data.frontier_node_count += 1
            data.visited.add(child_state)  # Add state to visited set
    return node, False
    
def greedy_step(grid_data: GridData, data: TreeData):
    node = data.queue.pop(0)
    if is_solution(grid_data.grid, node.value.boxes_positions, node.value.player_position):
        return node, True
    aux_grid_data = grid_data.copy()
    aux_grid_data.player_position = node.value.player_position
    aux_grid_data.boxes_positions = node.value.boxes_positions
    explore_node(node, aux_grid_data)
    data.expanded_node_count += 1
    data.frontier_node_count -= 1
    for child in node.children:
        # TODO hash
        child_state = (child.value.player_position, tuple(sorted(child.value.boxes_positions)))
        child_grid_data = grid_data.copy()
        if child_state not in data.visited:  # Check if state has been visited
            data.queue.append(child)
            data.frontier_node_count += 1
            data.visited.add(child_state)  # Add state to visited set
    data.queue.sort(key=lambda x: x.value.heuristic)
    return node, False

# Decide if the game has been solved
def is_solution(grid, boxes_positions, player_position):
    return all([grid[coordinate.row][coordinate.column] == GridElement.OBJECTIVE for coordinate in boxes_positions])

def calculate_heuristic(objective_positions, boxes_positions):
        return sum([min([abs(obj.row - box.row) + abs(obj.column - box.column) for obj in objective_positions]) for box in boxes_positions])

def main():
    grid_data = load_grid_from_file('grid.json')

    Sokoban(SCREEN_TITLE, grid_data)
    arcade.run()

if __name__ == "__main__":
    main()