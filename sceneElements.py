import math
import numpy as np
import matplotlib.pyplot as plt
import cv2
import time


class Light:
    def __init__(self, xPosition, yPosition, direction, strength, spreadAngle, width, color, horizontalSize, verticalSize):
        self.colorDictionary = {
            "red" : np.array([1.0, 0.0, 0.0]),
            "green" : np.array([0.0, 1.0, 0.0]),
            "blue" : np.array([0.0, 0.0, 1.0]),
            "yellow" : np.array([1.0, 1.0, 0.0]),
            "cyan" : np.array([0.0, 1.0, 1.0]),
            "magenta" : np.array([1.0, 0.0, 1.0]),
            "white" : np.array([1.0, 1.0, 1.0])
        }
        self.position = np.array([xPosition, yPosition])
        self.direction = direction #angle in degrees 0 = right, 90 = up, between -180 and +180
        self.strength = strength #0 to 11
        self.spreadAngle = spreadAngle #angle in degrees
        self.minVisibleAngle = direction - spreadAngle / 2
        self.maxVisibleAngle = direction + spreadAngle / 2
        self.width = width / math.sin(-direction * math.pi / 180)
        if color in self.colorDictionary:
            self.color = self.colorDictionary[color]
        else:
            print("Error: Colour " + str(color) + " is invalid")
            self.color = self.colorDictionary["white"]
        
        self.color *= strength / 11.0

        self.horizontalSize = horizontalSize
        self.verticalSize = verticalSize

        self.lightScreen = self.getNewLightScreen()
        self.changed = False
    
    def getNewLightScreen(self):
        newLightScreen = np.zeros([self.horizontalSize, self.verticalSize, 3])
        if self.minVisibleAngle <= -180:
            leftEdge = 0
            leftStep = 0
            # print(1)
        else:
            leftEdge = float(self.position[0])
            leftStep = 1 / math.tan(self.minVisibleAngle / 180 * math.pi)
        
        # print(self.maxVisibleAngle)
        if self.maxVisibleAngle >= 0:
            rightEdge = self.horizontalSize
            rightStep = 0
        else:
            rightEdge = float(self.position[0] + self.width)
            rightStep = 1 / math.tan(self.maxVisibleAngle / 180 * math.pi)
            # print(2)

        for y in range(self.verticalSize - 1, -1, -1):
            # print(str(leftEdge) + " " +  str(rightEdge) + " " + str(y))
            newLightScreen[int(leftEdge):int(rightEdge), y] = self.color
            leftEdge -= leftStep
            if leftEdge <= 0:
                leftEdge = 0
                leftStep = 0
            elif leftEdge >= self.horizontalSize:
                break
            
            rightEdge -= rightStep
            if rightEdge >= self.horizontalSize:
                rightEdge = self.horizontalSize
                rightStep = 0
            elif rightEdge <= 0:
                break
        
        return newLightScreen

    def getColor(self):
        return self.color
    
    def getLightScreen(self):
        if self.changed:
            self.lightScreen = self.getNewLightScreen()
        return self.lightScreen



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



class SmokeScreen:
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
    
    def getSmokeScreen(self):
        return self.smokeGrid

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


class Background:
    def __init__(self, horizontalSize, verticalSize):
        self.horizontalSize = horizontalSize
        self.verticalSize = verticalSize
        self.image = np.zeros([horizontalSize, verticalSize, 3])

    def getBackground(self):
        return self.image

    def getColor(self, position):
        # print(position)
        return self.image[position[1]][position[0]]
    
    def setBackground(self, imageLocation):
        image = None
        
        try:
            image = plt.imread(imageLocation)
            image = image[:,:,:3]
            image = cv2.resize(image, [self.horizontalSize, self.verticalSize])
            image = image.swapaxes(0, 1)
            self.image = image
            # print([self.horizontalSize, self.verticalSize])
        except FileNotFoundError:
            print("File not Found")
        except:
            print("File Invalid")
            self.image = np.zeros([self.horizontalSize, self.verticalSize, 3])



class Object:
    def __init__(self, imageLocation, rotation, horizontalPosition, verticalPosition, horizontalSize, screenHorizontalSize, screenVerticalSize):
        self.horizontalPosition = horizontalPosition
        self.verticalPosition = verticalPosition
        self.horizontalSize = horizontalSize
        self.screenHorizontalSize = screenHorizontalSize
        self.screenVerticalSize = screenVerticalSize
        try:
            image = plt.imread(imageLocation)
            image = np.rot90(image, rotation + 2, (0, 1))
            if image.shape[2] == 3:
                image = np.append(image, 1.0, 3)
            
            self.verticalSize = int(horizontalSize / image.shape[1] * image.shape[0])
            image = cv2.resize(image, [horizontalSize, self.verticalSize])
            self.image = image.swapaxes(0, 1)
        except:
            print("File Invalid")
            self.image = np.zeros([horizontalSize, horizontalSize, 4])
            self.verticalSize = horizontalSize
    
    def getObjectScreen(self):
        screen = np.zeros([self.screenHorizontalSize, self.screenVerticalSize, 4])
        # if self.horizontalPosition + self.horizontalSize < self.screenHorizontalSize:
        #     maxX = self.horizontalSize
        # else:
        #     maxX = self.screenHorizontalSize - self.horizontalPosition
        minX = max(0, -self.horizontalPosition)
        maxX = min(self.horizontalSize, self.screenHorizontalSize - self.horizontalPosition)
        maxX = max(0, maxX)
        dX = maxX - minX
        
        
        minY = max(0, -self.verticalPosition)
        maxY = min(self.verticalSize, self.screenVerticalSize - self.verticalPosition)
        maxY = max(0, maxY)
        dY = maxY - minY
        
        xPos = max(0, self.horizontalPosition)
        xPos = min(xPos, self.screenHorizontalSize)

        yPos = max(0, self.verticalPosition)
        yPos = min(yPos, self.screenVerticalSize)
        # print(str(xPos) + " " + str(yPos))

        screen[xPos:(xPos + dX), yPos:(yPos + dY)] = self.image[minX:maxX, minY:maxY]
        return screen

class Scene:
    def __init__(self, horizontalSize, verticalSize, baseSmoke):
        self.horizontalSize = horizontalSize
        self.verticalSize = verticalSize
        self.lightList = []
        self.background = Background(horizontalSize, verticalSize)
        self.smoke = SmokeScreen(horizontalSize, verticalSize, baseSmoke)
        self.objectList = []
    
    def addLight(self, xPosition, direction, strength, spreadAngle, width, color):
        self.lightList.append(Light(xPosition, self.verticalSize, direction, strength, spreadAngle, width, color, self.horizontalSize, self.verticalSize))

    def addSmokeMachine(self, location, size, strength):
        self.smoke.addSmokeMachine(location, size, strength)
    
    def addObject(self, imageLocation, rotation, horizontalPosition, verticalPosition, horizontalSize):
        self.objectList.append(Object(imageLocation, rotation, horizontalPosition, verticalPosition, horizontalSize, self.horizontalSize, self.verticalSize))

    def setBackground(self, imageLocation):
        self.background.setBackground(imageLocation)

    def render(self):
        # start = time.monotonic()
        self.smoke.updateSmokeGrid()
        # print(time.monotonic() - start)
        
        lightScreen = np.zeros([self.horizontalSize, self.verticalSize, 3])
        for light in self.lightList:
            lightScreen += light.getLightScreen()
        
        smokeScreen = self.smoke.getSmokeScreen()
        smokeScreen = np.stack([smokeScreen, smokeScreen, smokeScreen], -1)
        # smokeScreen = np.array([smokeScreen, smokeScreen, smokeScreen])
        litSmokeScreen = smokeScreen * lightScreen

        backdrop = self.background.getBackground()
        backdrop = np.fliplr(backdrop)
 
        for object in self.objectList:
            objectScreen = object.getObjectScreen()
            alphaMask = objectScreen[:, :, 3]
            alphaMask = np.stack([alphaMask, alphaMask, alphaMask], -1)
            objectScreen = objectScreen[:, :, :3]
            backdrop = alphaMask * objectScreen + (1.0 - alphaMask) * backdrop

        litBackdrop = lightScreen * backdrop* (1 - smokeScreen)


        output = litSmokeScreen + litBackdrop


        output /= max(1, output.max())
        # print("Max Colour: " + str(output.max()))

        output = np.swapaxes(output, 0, 1)
        # output = np.rot90(output, 1, [0, 1])
        # output = np.flipud(output)

        return output
    
