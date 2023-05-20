import math
import numpy as np
import matplotlib.pyplot as plt
import cv2
import time

class end(Exception):
    pass

def lerp(min, max, fraction):
    #Returns a value between min and max, linearly proportional to fraction
    return min * (1 - fraction) + max * fraction

class Light:
    def __init__(self, xPosition, yPosition, direction, strength, spreadAngle, width, color, instructionSet, horizontalSize, verticalSize):
        self.position = np.array([xPosition, yPosition])
        self.setDirection(direction)
        self.setStrength(strength)
        self.setSpreadAngle(spreadAngle) #angle in degrees
        self.setWidth(width)

        self.instructionIndex = 0
        self.instructionSet = instructionSet
        self.time = 0
        self.halted = False

        self.horizontalSize = horizontalSize
        self.verticalSize = verticalSize
        self.setColor(color)
        self.lightScreen = self.getNewLightScreen()
        self.changed = False
    
    def getNewLightScreen(self):
        minVisibleAngle = self.direction - self.spreadAngle / 2
        maxVisibleAngle = self.direction + self.spreadAngle / 2
        newLightScreen = np.zeros([self.horizontalSize, self.verticalSize, 3])
        if minVisibleAngle <= -180:
            leftEdge = 0
            leftStep = 0
            # print(1)
        else:
            leftEdge = float(self.position[0])
            leftStep = 1 / math.tan(minVisibleAngle / 180 * math.pi)
        
        # print(self.maxVisibleAngle)
        if maxVisibleAngle >= 0:
            rightEdge = self.horizontalSize
            rightStep = 0
        else:
            rightEdge = float(self.position[0] + self.width)
            rightStep = 1 / math.tan(maxVisibleAngle / 180 * math.pi)
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
    
    def setColor(self, color):
        colorDictionary = {
            "red" : np.array([1.0, 0.0, 0.0]),
            "green" : np.array([0.0, 1.0, 0.0]),
            "blue" : np.array([0.0, 0.0, 1.0]),
            "yellow" : np.array([1.0, 1.0, 0.0]),
            "cyan" : np.array([0.0, 1.0, 1.0]),
            "magenta" : np.array([1.0, 0.0, 1.0]),
            "white" : np.array([1.0, 1.0, 1.0])
        }
        if color in colorDictionary:
            self.color = colorDictionary[color]
        else:
            print("Error: Colour " + str(color) + " is invalid")
            self.color = colorDictionary["white"]
        
        self.color *= self.strength / 11.0

        self.changed = True

    def setDirection(self, direction):
        self.direction = direction
        self.changed = True


    def setWidth(self, width):
        self.width = width / math.sin(-self.direction * math.pi / 180)
        self.changed = True

    def setSpreadAngle(self, spreadAngle):
        self.spreadAngle = spreadAngle
        self.changed = True

    def setStrength(self, strength):
        self.strength = strength
        self.changed = True

    def update(self, dt):
        #Instruction Set:Move to, Loop To(Row Index), Hold, Stop, End(Kills whole program)
        if self.halted == False:
            self.time += dt
            instruction = self.instructionSet.iloc[self.instructionIndex]
            if self.time > instruction.get("End Time"):
                self.instructionIndex += 1# print(instruction)
            currentInstruction = instruction.get("Instruction")
            if currentInstruction == None:
                self.halted = True
            elif currentInstruction == "Move To":
                remainingTime = instruction.get("End Time") - self.time
                if remainingTime == 0:
                    moveFraction = 1
                else:
                    moveFraction = min(dt / remainingTime, 1)
                self.setColor(instruction.get("Color"))
                self.setDirection(lerp(self.direction, instruction.get("Direction"), moveFraction))
                self.setSpreadAngle(lerp(self.spreadAngle, instruction.get("Spread Angle"), moveFraction))
                self.setStrength(lerp(self.strength, instruction.get("Strength"), moveFraction))
                self.setWidth(lerp(self.width, instruction.get("Width"), moveFraction))

            elif currentInstruction == "Loop To":
                self.instructionIndex = int(instruction.get("Loop To Index"))
                if self.instructionIndex == 0:
                    self.time = 0
                else:
                    self.time = instruction.get("End Time").get(self.instructionIndex - 1)
            elif currentInstruction == "Hold":
                pass
            elif currentInstruction == "Stop":
                self.halted = True
            elif currentInstruction == "End":
                raise(end)




class smokeMachine:
    def __init__(self, position, strength, direction, speed, instructionSet):
        self.position = np.array(position)
        self.setStrength(strength)
        self.setDirection(direction)
        self.setSpeed(speed)
        self.instructionSet = instructionSet
        self.halted = False
        self.time = 0
        self.instructionIndex = 0
        # self.minX = max(location[0] - size, 0)
        # self.maxX = min(location[0] + size, horizontalSize)
        # self.minY = max(location[1] - size, 0)
        # self.maxY = min(location[1] + size, verticalSize)
    
    def getNewSmoke(self):
        #Smoke[0] is positions
        #Smoke[1] is velocities
        angleSpread = 30.0
        speedSpread = 100.0
        positionSpread = 20
        smokeAngles = self.direction + angleSpread * (np.random.random([self.strength]) * 2 - 1)
        # print(np.max(smokeAngles))
        smokeSpeeds = self.speed + speedSpread * np.random.random([self.strength])
        smokePositions = (np.random.random([self.strength, 2]) - 0.5)  * positionSpread + self.position
        smokeVelocities = np.array([np.cos(np.deg2rad(smokeAngles)), np.sin(np.deg2rad(smokeAngles))]) * smokeSpeeds
        smokeVelocities = np.swapaxes(smokeVelocities, 0, 1)
        # print(smokePositions)
        # print(smokeVelocities)
        newSmoke = np.array([smokePositions, smokeVelocities])
        return newSmoke
    # def setSmoke(self, smokeGridView):
    #     smokeGridView[self.minX:self.maxX, self.minY:self.maxY] = self.strength / 11 * 0.8

    def setStrength(self, strength):
        self.strength = int(strength)
    
    def setDirection(self, direction):
        self.direction = direction
    
    def setSpeed(self, speed):
        self.speed = speed
    
    def update(self, dt):
        #Instruction Set:Move to, Loop To(Row Index), Hold, Stop, End(Kills whole program)
        if self.halted == False:
            self.time += dt
            instruction = self.instructionSet.iloc[self.instructionIndex]
            # print(instruction)
            if self.time > instruction.get("End Time"):
                self.instructionIndex += 1            
            currentInstruction = instruction.get("Instruction")
            if currentInstruction == None:
                self.halted = True
            elif currentInstruction == "Move To":
                remainingTime = instruction.get("End Time") - self.time
                if remainingTime == 0:
                    moveFraction = 1
                else:
                    moveFraction = min(dt / remainingTime, 1)
                self.setDirection(lerp(self.direction, instruction.get("Direction"), moveFraction))
                self.setStrength(lerp(self.strength, instruction.get("Strength"), moveFraction))
                self.setSpeed(lerp(self.speed, instruction.get("Speed"), moveFraction))

            elif currentInstruction == "Loop To":
                self.instructionIndex = int(instruction.get("Loop To Index"))
                if self.instructionIndex == 0:
                    self.time = 0
                else:
                    self.time = instruction.get("End Time").get(self.instructionIndex - 1)
            elif currentInstruction == "Hold":
                pass
            elif currentInstruction == "Stop":
                self.halted = True
            elif currentInstruction == "End":
                raise(end)

class SmokeScreen:
    def __init__(self, horizontalSize, verticalSize, baseSmoke):
        self.horizontalSize = horizontalSize
        self.verticalSize = verticalSize
        self.baseSmoke = baseSmoke
        self.smokeScreen = np.zeros([horizontalSize, verticalSize]) + baseSmoke
        self.particleSize = 10
        self.smokeMachines = []
        self.smokeParticlePositions = np.array([[]])
        self.smokeParticleVelocities = np.array([[]])
        self.smokeParticleIntensities = np.array([])
        self.velocityScreen = self.getNewVelocityScreen()

    
    def addSmokeMachine(self, position, strength, direction, speed, instructionSet):
        self.smokeMachines.append(smokeMachine(position, strength, direction, speed, instructionSet))
    
    def getSmoke(self, location):
        return self.smokeScreen[location[0]][location[1]]
    
    def getSmokeScreen(self):
        return self.smokeScreen

    def getNewVelocityScreen(self):
        rescaleFactor = 100
        velocityScreen = np.random.random([int(self.horizontalSize / rescaleFactor), int(self.verticalSize / rescaleFactor), 2])
        velocityScreen = cv2.resize(velocityScreen, [self.verticalSize, self.horizontalSize])[:, :, :2] * 2 - 1
        velocityScreen *= 200
        # print("max: " + str(np.max(velocityScreen)))
        # print("min: " + str(np.min(velocityScreen)))
        return velocityScreen
    

    def updateSmokeScreen(self, dt):
        # tempScreen = self.smokeScreen.copy()
        # print(self.velocityScreen.shape)
        # print(self.smokeParticlePositions.size)
        for smokeMachine in self.smokeMachines:
            smokeMachine.update(dt)
        

        if self.smokeParticlePositions.size != 0:
            #if particles exist move particles
            velocityRetention = 0.94
            velocityRandom = 0.03
            self.smokeParticleVelocities *= velocityRetention
            self.smokeParticleVelocities += 20 *  velocityRandom * np.random.normal(size = self.smokeParticleVelocities.shape)

            particleLife = 10.0
            self.smokeParticleIntensities -= dt / particleLife

            for i in range(0, len(self.smokeParticlePositions)):
                # print(self.smokeParticlePositions[i].astype(int))
                position = self.smokeParticlePositions[i].astype(int)
                self.smokeParticleVelocities[i] += (1 - velocityRetention -velocityRandom) * self.velocityScreen[position[0], position[1]]
            self.smokeParticlePositions += self.smokeParticleVelocities * dt

            #create new particles
            for smokeMachine in self.smokeMachines:
                newSmokeParticles = smokeMachine.getNewSmoke()
                # print(newSmokeParticles[0].shape)
                # print(self.smokeParticlePositions)
                self.smokeParticlePositions = np.append(self.smokeParticlePositions, newSmokeParticles[0], 0)
                self.smokeParticleVelocities = np.append(self.smokeParticleVelocities, newSmokeParticles[1], 0)
                self.smokeParticleIntensities = np.append(self.smokeParticleIntensities, np.ones([newSmokeParticles.shape[1]]))
        else:
            #if no particles exist create new particles
            for smokeMachine in self.smokeMachines:
                newSmokeParticles = smokeMachine.getNewSmoke()
                # print(newSmokeParticles[0].shape)
                # print(self.smokeParticlePositions)
                self.smokeParticlePositions = newSmokeParticles[0]
                self.smokeParticleVelocities = newSmokeParticles[1]
                self.smokeParticleIntensities = np.ones([newSmokeParticles.shape[1]])

        
        # print(self.smokeGrid)
        # print(self.smokeParticleIntensities.shape, self.smokeParticlePositions.shape)

        newSmokeScreen = np.zeros([self.horizontalSize + 2 * self.particleSize, self.verticalSize + 2 * self.particleSize]) + self.baseSmoke
        # print(self.smokeParticlePositions.size)
        if self.smokeParticlePositions.size > 0:
            toDelete = []
            for i in range(0, len(self.smokeParticlePositions)):
                smokeParticlePosition = self.smokeParticlePositions[i]
                # print(len(smokeParticlePosition))
                if min(smokeParticlePosition) < 0 or smokeParticlePosition[0] > self.horizontalSize or smokeParticlePosition[1] > self.verticalSize or self.smokeParticleIntensities[i] <= 0:
                    toDelete.append(i)
                else:
                    endPosition = smokeParticlePosition + self.particleSize
                    # print(self.smokeParticleIntensities[i])
                    newSmokeScreen[int(smokeParticlePosition[0]):int(endPosition[0]), int(smokeParticlePosition[1]):int(endPosition[1])] += self.smokeParticleIntensities[i]

            self.smokeParticlePositions = np.delete(self.smokeParticlePositions, toDelete, 0)
            self.smokeParticleVelocities = np.delete(self.smokeParticleVelocities, toDelete, 0)
            self.smokeParticleIntensities = np.delete(self.smokeParticleIntensities, toDelete, 0)


        blurSize = 40
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
    def __init__(self, imageLocation, rotation, position, horizontalSize, instructionSet, screenHorizontalSize, screenVerticalSize):
        self.setPosition(position)
        self.horizontalSize = horizontalSize
        self.screenHorizontalSize = screenHorizontalSize
        self.screenVerticalSize = screenVerticalSize
        
        self.instructionSet = instructionSet
        self.halted = False
        self.time = 0
        self.instructionIndex = 0
        
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
    
    def setPosition(self, position):
        self.horizontalPosition = int(position[0])
        self.verticalPosition = int(position[1])
    
    def update(self, dt):
        #Instruction Set:Move to, Loop To(Row Index), Hold, Stop, End(Kills whole program)
        if self.halted == False:
            self.time += dt
            instruction = self.instructionSet.iloc[self.instructionIndex]
            # print(instruction)
            if self.time > instruction.get("End Time"):
                self.instructionIndex += 1
            
            currentInstruction = instruction.get("Instruction")
            if currentInstruction == None:
                self.halted = True
            elif currentInstruction == "Move To":
                remainingTime = instruction.get("End Time") - self.time
                if remainingTime == 0:
                    moveFraction = 1
                else:
                    moveFraction = min(dt / remainingTime, 1)
                horizontalPosition = lerp(self.horizontalPosition, instruction.get("Horizontal Position"), moveFraction)
                verticalPosition = lerp(self.verticalPosition, instruction.get("Vertical Position"), moveFraction)
                self.setPosition([horizontalPosition, verticalPosition])
            
            elif currentInstruction == "Loop To":
                self.instructionIndex = int(instruction.get("Loop To Index"))
                if self.instructionIndex == 0:
                    self.time = 0
                else:
                    self.time = instruction.get("End Time").get(self.instructionIndex - 1)
            elif currentInstruction == "Hold":
                pass
            elif currentInstruction == "Stop":
                self.halted = True
            elif currentInstruction == "End":
                raise(end) 

class Scene:
    def __init__(self, horizontalSize, verticalSize, baseSmoke):
        self.horizontalSize = horizontalSize
        self.verticalSize = verticalSize
        self.lightList = []
        self.background = Background(horizontalSize, verticalSize)
        self.smoke = SmokeScreen(horizontalSize, verticalSize, baseSmoke)
        self.objectList = []
    
    def addLight(self, xPosition, direction, strength, spreadAngle, width, color, instructionSet):
        self.lightList.append(Light(xPosition, self.verticalSize, direction, strength, spreadAngle, width, color, instructionSet, self.horizontalSize, self.verticalSize))

    def addSmokeMachine(self, position, strength, direction, speed, instructionSet):
        self.smoke.addSmokeMachine(position, strength, direction, speed, instructionSet)
    
    def addObject(self, imageLocation, rotation, position, horizontalSize, instructionSet):
        self.objectList.append(Object(imageLocation, rotation, position, horizontalSize, instructionSet, self.horizontalSize, self.verticalSize))

    def setBackground(self, imageLocation):
        self.background.setBackground(imageLocation)

    def render(self, dt):
        # start = time.monotonic()
        self.smoke.updateSmokeScreen(dt)
        # print(time.monotonic() - start)
        
        lightScreen = np.zeros([self.horizontalSize, self.verticalSize, 3])
        for light in self.lightList:
            light.update(dt)
            lightScreen += light.getLightScreen()
        
        smokeScreen = self.smoke.getSmokeScreen()
        smokeScreen = np.stack([smokeScreen, smokeScreen, smokeScreen], -1)
        # smokeScreen = np.array([smokeScreen, smokeScreen, smokeScreen])
        litSmokeScreen = smokeScreen * lightScreen

        backdrop = self.background.getBackground()
        backdrop = np.fliplr(backdrop)

        for object in self.objectList:
            object.update(dt)
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
    
