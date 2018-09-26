import numpy as np

class Point:
    def __init__(self,x_init,y_init):
        self.x = x_init
        self.y = y_init

    def __repr__(self):
        return "".join(["(", str(self.x), ",", str(self.y), ")"])

