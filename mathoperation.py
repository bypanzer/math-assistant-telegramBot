import numpy as np

class MathOperation:
    def __init__(self, operation_init, width_init, height_init, x_init, y_init, isCorrect_init):
        self.operation = operation_init
        self.width = width_init
        self.height = height_init
        self.x = x_init
        self.y = y_init
        self.isCorrect = False
        
    def __repr__(self):
        return "".join(["(", str(self.operation), ")"])    



