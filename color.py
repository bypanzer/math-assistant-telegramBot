from PIL import Image, ImageOps
import numpy as np
import cv2

str = "22 \\times 4 = 88"
if "\\times" in str:
	print("yes")
else:
	print("no")
str = str.replace(" ", "")

print(str)
