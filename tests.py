import numpy as np

class Point:
    def __init__(self,x_init,y_init):
        self.x = x_init
        self.y = y_init

    def __repr__(self):
        return "".join(["(", str(self.x), ",", str(self.y), ")"])

p1 = Point(1, 2)
p2 = Point(3, 4)

arr = np.array([])
arr = np.append(arr, p1)
arr = np.append(arr, p2)

print(arr)
