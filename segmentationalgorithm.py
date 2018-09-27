import numpy as np
from point import Point
from mathoperation import MathOperation

def calculateHorizontalForegrounds(edges_arr, width, height):
        foregrounds = np.array([])
        foregroundAmount = 0
        for row in range(height):
            for column in range(width):
                if edges_arr[row][column] == 255:
                    foregroundAmount += 1
            if foregroundAmount > 0:
                foregroundAmount = 1        
            foregrounds = np.append(foregrounds, foregroundAmount)
            foregroundAmount = 0
        return foregrounds
    

def calculateSum(foregrounds):
        sums = np.array([])
        sumIndex = 0
        cons = foregrounds[0]
        if cons == 0:
            sums = np.append(sums, Point(1, 0))
        else:
            sums = np.append(sums, Point(1, 1))

        for index in range(foregrounds.size):
            if foregrounds[index] == cons:
                sums[sumIndex].x += 1
            else:
                sumIndex += 1
                if foregrounds[index] == 0:
                    sums = np.append(sums, Point(1, 0))
                else:
                    sums = np.append(sums, Point(1, 1))
                cons = foregrounds[index]
        if sums.size <= 1:
            print("sum return None")
            return None
        else:
            return sums
    
def deleteWhiteNoise(sums, threshold, leftAndRightBlackValues):
        for index in range(1, sums.size - 1):
            if sums[index].y == 1:
                if sums[index].x <= threshold: #10 -> withThreshold
                    if sums[index - 1].x > leftAndRightBlackValues or sums[index + 1].x > leftAndRightBlackValues: #15 -> leftAndRightBlackValues
                        sums[index].y = 0
        if sums[0].y == 1:
            sums[0].y = 0
        return sums

    
def mergeConsecutiveEqualsNumbers(sums):
        sums2 = np.array([])
        current = 0
        cons2 = sums[0].y
        sums2 = np.append(sums2, sums[0])

        for index in range(1, sums.size):
            if sums[index].y != cons2:
                cons2 = sums[index].y
                sums2 = np.append(sums2, sums[index])
                current += 1
            else:
                sums2[current].x = sums2[current].x + sums[index].x

        return sums2


def deleteBlackNoise(sums2, blackNoise, whiteNoise, noiseForFirstElement):
    if sums2.size > 1:
        for index in range(1, sums2.size - 1):
            if sums2[index].y == 0:
                if sums2[index].x <= blackNoise:
                    if sums2[index - 1].x >= whiteNoise or sums2[index + 1].x >= whiteNoise:
                        sums2[index].y = 1
        if sums2[0].y == 0:
            if sums2[0].x <= noiseForFirstElement:
                sums2[0].y = 1

    return sums2


def drawHorizontalLines(sums2, edges_arr, width, height):
    startDrawing = 0
    for index2 in range(sums2.size):
        if sums2[index2].y == 0:
            for row in range(startDrawing, sums2[index2].x + startDrawing):
                for column in range(width):
                    if row < height and column < width:
                        edges_arr[row][column] = 255 #white color
        startDrawing = startDrawing + sums2[index2].x

        
        
def calculateVerticalForegrounds(edges_arr, width, start, stop):
        foregrounds2 = np.array([])
        foregroundAmount = 0
        for col in range(width):
            for row in range(start, stop):
                if edges_arr[row][col] == 255:
                    foregroundAmount += 1
            if foregroundAmount > 0:
                foregroundAmount = 1
            foregrounds2 = np.append(foregrounds2, foregroundAmount)
            foregroundAmount = 0
        return foregrounds2
    
    
def drawVerticalLines(sums3, edges_arr, width, height, start, stop, mathOperations):
        startDrawing = 0
        for index in range(sums3.size):
            if sums3[index].y == 0:
                for col in range(startDrawing, sums3[index].x + startDrawing):
                    for row in range(start, stop):
                        if row < height and col < width:
                            edges_arr[row][col] = 255 #white color
            else:
                mathOp = MathOperation("undefined", sums3[index].x, stop - start, startDrawing, start, False)
                mathOperations = np.append(mathOperations, mathOp)
            startDrawing = startDrawing + sums3[index].x
        
