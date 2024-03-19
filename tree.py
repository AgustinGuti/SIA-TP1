
class NodeValue:
    def __init__(self, player_position, boxes_position: list, direction, heuristic=0, depth=0):
        self.player_position = player_position
        self.boxes_positions = boxes_position
        self.heuristic = heuristic
        self.depth = depth
        self.direction = direction

    def __eq__(self, other):
        return self.player_position == other.player_position and self.boxes_positions == other.boxes_positions
    
    def __hash__(self):
        return hash((self.player_position, tuple(sorted(self.boxes_positions))))

    def __str__(self) -> str:
        return f"Player: {self.player_position}, Boxes: {self.boxes_positions}, Heuristic: {self.heuristic}, Depth: {self.depth}"
    
    def __lt__(self, other):
        return self.heuristic < other.heuristic
    
    def __repr__(self) -> str:
        return self.__str__()

class Node:
    def __init__(self, value):
        self.value = value
        self.parent = None
        self.children = []

    def add_child(self, child_node):
        child_node.parent = self
        self.children.append(child_node)

    def __repr__(self, level=0):
        ret = "\t" * level + repr(self.value) + "\n"
        for child in self.children:
            ret += child.__repr__(level + 1)
        return ret
    
    def __lt__ (self, other):
        return self.value < other.value
    
    def __str__(self):
        return self.__repr__()
    
    def __eq__(self, other):
        return self.value.__hash__() == other.value.__hash__()
    
    def __hash__(self):
        return self.value.__hash__()