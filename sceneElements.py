import math
import numpy as np
import matplotlib.pyplot as plt
import cv2


class light:
    def __init__(self, xPosition, direction, strength, spreadAngle, color):
        self.colorDictionary = {
            "red" : np.array([1.0, 0.0, 0.0]),
            "green" : np.array([0.0, 1.0, 0.0]),
            "blue" : np.array([0.0, 0.0, 1.0]),
            "yellow" : np.array([1.0, 1.0, 0.0]),
            "cyan" : np.array([0.0, 1.0, 1.0]),
            "magenta" : np.array([1.0, 0.0, 1.0]),
            "white" : np.array([1.0, 1.0, 1.0])
        }
        self.position = np.array([xPosition, 288])
        self.direction = direction #angle in degrees 0 = right, 90 = up
        self.strength = strength #0 to 11
        self.spreadAngle = spreadAngle #angle in degrees
        self.minVisibleAngle = direction - spreadAngle / 2 + 180
        self.maxVisibleAngle = direction + spreadAngle / 2 + 180
        if color in self.colorDictionary:
            self.color = self.colorDictionary[color]
        else:
            print("Error: Colour " + str(color) + " is invalid")
            self.color = self.colorDictionary["white"]
        
        self.color *= strength / 11.0
    
    def getAngle(self, otherPosition):
        dY = self.position[1] - otherPosition[1]
        dX = self.position[0] - otherPosition[0]
        angle = 0.0
        if dX == 0:
            if dY > 0:
                angle = 90.0
            else:
                angle = 270.0
        elif dY == 0:
            if dX > 0:
                angle = 0.0
            else:
                angle = 180.0
        else:
            angle = math.atan(dY / dX) * 360.0 / (2 * math.pi)
        
            if angle <= 0:
                angle += 180
            
            if dY < 0:
                angle += 180
        
        return angle

    def isLit(self, cellPosition):
        angle = self.getAngle(cellPosition)
        if angle > self.minVisibleAngle and angle < self.maxVisibleAngle:
            return True
        else:
            return False
    
    def getColor(self):
        return self.color



class smokeMachine:
    def __init__(self, location, size, strength, horizontalSize, verticalSize):
        self.location = np.array(location)
        self.size = size
        self.strength = strength
        self.minX = max(location[0] - size, 0)
        self.maxX = min(location[0] + size, horizontalSize)
        self.minY = max(location[1] - size, 0)
        self.maxY = min(location[1] + size, verticalSize)
    
    def setSmoke(self, smokeGridView):
        smokeGridView[self.minX:self.maxX, self.minY:self.maxY] = self.strength / 11 * 0.8



class smokeScreen:
    def __init__(self, horizontalSize, verticalSize, baseSmoke):
        self.horizontalSize = horizontalSize
        self.verticalSize = verticalSize
        self.smokeGrid = np.zeros([horizontalSize, verticalSize]) + baseSmoke
        self.updateRange = 20
        self.smokeMachines = []
    
    def addSmokeMachine(self, location, size, strength):
        self.smokeMachines.append(smokeMachine(location, size, strength, self.horizontalSize, self.verticalSize))
    
    def getSmoke(self, location):
        return self.smokeGrid[location[0]][location[1]]

    def updateSmokeGrid(self):
        tempGrid = self.smokeGrid.copy()
        
        for smokeMachine in self.smokeMachines:
            smokeMachine.setSmoke(tempGrid.view())
        # print(self.smokeGrid)

        for x in range(0, self.horizontalSize):
            minX = max(x - self.updateRange, 0)
            maxX = min(x + self.updateRange, self.horizontalSize)
            
            for y in range(0, self.verticalSize):
                minY = max(y - self.updateRange, 0)
                maxY = min(y + self.updateRange, self.verticalSize)
                # print(str(minX) + str(maxX) + str(minY) + str(maxY))
                self.smokeGrid[x][y] = tempGrid[minX:maxX, minY:maxY].mean()
        
        # print(self.smokeGrid)


class cell:
    def __init__(self, position):
        self.position = np.array(position)

    def getColor(self, lightList, background, smoke):
        lightColor = np.array([0.0, 0.0, 0.0])

        for light in lightList:
            if light.isLit(self.position):
                lightColor += light.getColor()

        smokeStrength = smoke.getSmoke(self.position)
        # print(smokeStrength)
        smokeColor = lightColor * smokeStrength
        
        backgroundColor = np.array(background.getColor(self.position))
        backgroundColor *= 1 - smokeStrength
        backgroundColor *= lightColor

        color = smokeColor + backgroundColor

        # Color proportional to angle from light 0
        # light = lightList[0]
        # scale = light.getAngle(self.position) / 360.0       
        # myColor = np.array([scale, scale, scale])

        return color

class background:
    def __init__(self, imageLocation, desiredSize):
        self.image = np.zeros([desiredSize[0], desiredSize[1], 3])
        tempImage  = None
        try:
            tempImage = plt.imread(imageLocation)
            tempImage = tempImage[:,:,:3]

        except FileNotFoundError:
            print("File not Found")
        
        if tempImage.any() != None:
            self.image = cv2.resize(tempImage, desiredSize)
        
        # print(len(self.image))
    
    def getColor(self, position):
        # print(position)
        return self.image[position[1]][position[0]]

class scene:
    def __init__(self, horizontalSize, verticalSize, baseSmoke):
        self.horizontalSize = horizontalSize
        self.verticalSize = verticalSize
        self.lightList = []
        self.background = np.zeros([horizontalSize, verticalSize, 3])
        self.cells = np.empty((horizontalSize, verticalSize), dtype=object)
        self.smoke = smokeScreen(horizontalSize, verticalSize, baseSmoke)

        for x in range(0, horizontalSize):
            for y in range(0, verticalSize):
                self.cells[x][y] = cell(np.array([x, y]))
    
    def addLight(self, position, direction, strength, spreadAngle, color):
        self.lightList.append(light(position, direction, strength, spreadAngle, color))

    def addSmokeMachine(self, location, size, strength):
        self.smoke.addSmokeMachine(location, size, strength)
    
    def setBackground(self, imageLocation):
        self.background = background(imageLocation, [self.horizontalSize, self.verticalSize])

    def render(self):
        self.smoke.updateSmokeGrid()

        output = np.zeros([self.verticalSize, self.horizontalSize, 3])
        for x in range(0, self.horizontalSize):
            for y in range(0, self.verticalSize):
                newColor = self.cells[x][y].getColor(self.lightList, self.background, self.smoke)
                output[y][x] = newColor
                # print(self.cells[x][y].getColor(self.lightList))
                
        output /= max(1, output.max())
        # print("Max Colour: " + str(output.max()))

        return output
    
