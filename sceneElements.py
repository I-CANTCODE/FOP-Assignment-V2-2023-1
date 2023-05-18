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
    def __init__(self, position, strength, velocity):
        self.position = np.array(position)
        self.strength = strength
        self.velocity = velocity
        # self.minX = max(location[0] - size, 0)
        # self.maxX = min(location[0] + size, horizontalSize)
        # self.minY = max(location[1] - size, 0)
        # self.maxY = min(location[1] + size, verticalSize)
    
    def getNewSmoke(self):
        #Smoke[0] is positions
        #Smoke[1] is velocities
        initialSpread = 10.0
        smokePositions = (np.random.random([self.strength, 2]) - 0.5)  * initialSpread + self.position
        velocitySpread = 2.0
        smokeVelocities = (np.random.random([self.strength, 2]) - 0.5) * velocitySpread + self.velocity
        newSmoke = np.array([smokePositions, smokeVelocities])
        return newSmoke
    # def setSmoke(self, smokeGridView):
    #     smokeGridView[self.minX:self.maxX, self.minY:self.maxY] = self.strength / 11 * 0.8



class SmokeScreen:
    def __init__(self, horizontalSize, verticalSize, baseSmoke):
        self.horizontalSize = horizontalSize
        self.verticalSize = verticalSize
        self.baseSmoke = baseSmoke
        self.smokeScreen = np.zeros([horizontalSize, verticalSize]) + baseSmoke
        self.particleSize = 20
        self.smokeMachines = []
        self.smokeParticlePositions = np.array([[]])
        self.smokeParticleVelocities = np.array([[]])
        self.velocityScreen = self.getNewVelocityScreen()

    
    def addSmokeMachine(self, location, strength, velocity):
        self.smokeMachines.append(smokeMachine(location, strength, velocity))
    
    def getSmoke(self, location):
        return self.smokeScreen[location[0]][location[1]]
    
    def getSmokeScreen(self):
        return self.smokeScreen

    def getNewVelocityScreen(self):
        rescaleFactor = 100
        maxVelocity = 10
        velocityScreen = 10 * np.random.random([int(self.horizontalSize / rescaleFactor), int(self.verticalSize / rescaleFactor), 2])
        velocityScreen = cv2.resize(velocityScreen, [self.verticalSize, self.horizontalSize])[:, :, :2]
        return velocityScreen
    

    def updateSmokeScreen(self):
        tempScreen = self.smokeScreen.copy()
        #move particles
        velocityRetention = 0.8
        self.smokeParticleVelocities *= velocityRetention
        # print(self.velocityScreen.shape)
        # print(self.smokeParticlePositions.size)
        if self.smokeParticlePositions.size != 0:
            for i in range(0, len(self.smokeParticlePositions)):
                # print(self.smokeParticlePositions[i].astype(int))
                position = self.smokeParticlePositions[i].astype(int)
                self.smokeParticleVelocities[i] += (1 - velocityRetention) * self.velocityScreen[position[0], position[1]]
            self.smokeParticlePositions += self.smokeParticleVelocities

            #create new particles
            for smokeMachine in self.smokeMachines:
                newSmokeParticles = smokeMachine.getNewSmoke()
                # print(newSmokeParticles[0].shape)
                # print(self.smokeParticlePositions)
                self.smokeParticlePositions = np.append(self.smokeParticlePositions, newSmokeParticles[0], 0)
                self.smokeParticleVelocities = np.append(self.smokeParticleVelocities, newSmokeParticles[1], 0)
        
        else:
            for smokeMachine in self.smokeMachines:
                newSmokeParticles = smokeMachine.getNewSmoke()
                # print(newSmokeParticles[0].shape)
                # print(self.smokeParticlePositions)
                self.smokeParticlePositions = newSmokeParticles[0]
                self.smokeParticleVelocities = newSmokeParticles[1]
        
        # print(self.smokeGrid)

        newSmokeScreen = np.zeros([self.horizontalSize + 2 * self.particleSize, self.verticalSize + 2 * self.particleSize]) + self.baseSmoke
        toDelete = []
        for i in range(0, len(self.smokeParticlePositions)):
            smokeParticlePosition = self.smokeParticlePositions[i]
            # print(smokeParticlePosition)
            if min(smokeParticlePosition) < 0 or max(smokeParticlePosition) > max(self.horizontalSize, self.verticalSize):
                toDelete.append(i)
            else:
                endPosition = smokeParticlePosition + self.particleSize
                # print(smokeParticlePosition)
                newSmokeScreen[int(smokeParticlePosition[0]):int(endPosition[0]), int(smokeParticlePosition[1]):int(endPosition[1])] += 1.0
        
        self.smokeParticlePositions = np.delete(self.smokeParticlePositions, toDelete, 0)
        self.smokeParticleVelocities = np.delete(self.smokeParticleVelocities, toDelete, 0)

        blurSize = 50
        newSmokeScreen = cv2.blur(newSmokeScreen[self.particleSize:-self.particleSize, self.particleSize:-self.particleSize], [blurSize, blurSize])
        self.smokeScreen =  np.clip(newSmokeScreen, 0, 1)

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

    def addSmokeMachine(self, location, strength, velocity):
        self.smoke.addSmokeMachine(location, strength, velocity)
    
    def addObject(self, imageLocation, rotation, horizontalPosition, verticalPosition, horizontalSize):
        self.objectList.append(Object(imageLocation, rotation, horizontalPosition, verticalPosition, horizontalSize, self.horizontalSize, self.verticalSize))

    def setBackground(self, imageLocation):
        self.background.setBackground(imageLocation)

    def render(self):
        # start = time.monotonic()
        self.smoke.updateSmokeScreen()
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
    
