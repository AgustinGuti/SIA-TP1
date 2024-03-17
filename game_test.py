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
    def __init__(self, title, grid_data: GridData):
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

        return super().update(delta_time)




def main():
    grid_data = load_grid_from_file('grid.json')

    Sokoban(SCREEN_TITLE, grid_data)
    arcade.run()

if __name__ == "__main__":
    main()