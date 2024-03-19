import json
from enum import Enum
from collections import namedtuple

# Define elements of the grid
class GridElement(Enum):
    EMPTY = 0
    FILLED = 1
    PLAYER = 2
    OBJECTIVE = 3
    BOX = 4

class Coordinate:
    def __init__(self, row, column):
        self.row = row
        self.column = column

    def __eq__(self, other):
        return self.row == other.row and self.column == other.column
    
    def __hash__(self):
        return hash((self.row, self.column))

    def __repr__(self):
        return f"({self.row}, {self.column})"

    def __str__(self):
        return self.__repr__()
    
    def __lt__(self, other):
        return self.row < other.row or (self.row == other.row and self.column < other.column)

    def move(self, direction):
        return Coordinate(self.row + direction[0], self.column + direction[1])

    def __lt__(self, other):
        return (self.row, self.column) < (other.row, other.column)

class GridData:
    def __init__(self, grid, player_position, boxes_positions, objectives_positions, grid_name = None):
        self.name = grid_name
        self.grid = grid
        self.player_position = player_position
        self.boxes_positions = boxes_positions
        self.objective_positions = objectives_positions

    def copy(self):
        return GridData(self.grid, self.player_position, self.boxes_positions, self.objective_positions, self.name)
    
    def __str__(self) -> str:
        string = ""
        for row in self.grid:
            for cell in row:
                if self.player_position == cell:
                    string += "@"
                elif cell in self.boxes_positions:
                    string += "$"
                elif cell == GridElement.OBJECTIVE:
                    string += "."
                elif cell == GridElement.FILLED:
                    string += "#"
                else:
                    string += " "
            string += "\n"
        return string

def validate_grid(grid_data):
    row_count = len(grid_data.grid)
    if row_count == 0:
        raise ValueError("Grid cannot be empty")
    column_count = len(grid_data.grid[0])
    objective_count = 0
    for row in range(len(grid_data.grid)):
        if len(grid_data.grid[row]) != column_count:
            raise ValueError("All rows in the grid must have the same length")
        for column in range(len(grid_data.grid[0])):
            if grid_data.grid[row][column] == GridElement.OBJECTIVE:
                objective_count += 1
    
    if objective_count != grid_data.boxes_positions.count:
        raise ValueError("There must be the same number of objectives as boxes in the grid")
    return True

def load_grid(data):
    grid = []
    player_position = None
    boxes_positions = []
    objectives_positions = []
    for line in data['grid']:
        row = []
        for char in line:
            if char == '#':
                row.append(GridElement.FILLED)
            elif char == '@':
                player_position = Coordinate(len(grid), len(row))
                row.append(GridElement.EMPTY)
            elif char == '.':
                row.append(GridElement.OBJECTIVE)
                objectives_positions.append(Coordinate(len(grid), len(row)))
            elif char == '$':
                boxes_positions.append(Coordinate(len(grid), len(row)))
                row.append(GridElement.EMPTY)
            else:
                row.append(GridElement.EMPTY)
        grid.append(row)
    data = GridData(grid, player_position, boxes_positions, objectives_positions, data['name'])
    # validate_grid(data)
    return data