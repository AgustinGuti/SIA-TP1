
class NodeValue:
    def __init__(self, player_position, boxes_position: list, direction, heuristic=0, depth=0):
        self.player_position = player_position
        self.boxes_positions = boxes_position
        self.heuristic = heuristic
        self.depth = depth
        self.direction = direction

    def __str__(self) -> str:
        return f"Player: {self.player_position}, Boxes: {self.boxes_positions}, Heuristic: {self.heuristic}, Depth: {self.depth}"
    
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
    
    def __str__(self):
        return self.__repr__()