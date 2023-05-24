import math
import numpy as np
import matplotlib.pyplot as plt
import cv2
from matplotlib.patches import Wedge, Polygon
from matplotlib.collections import PatchCollection

#Enables the render loop to be easily ended from anywhere in the program
class end(Exception):
    pass

#Returns a value between min and max, linearly proportional to fraction
def lerp(min, max, fraction):
    return min * (1 - fraction) + max * fraction



class Light:
    def __init__(self, xPosition, yPosition, direction, strength, spreadAngle, width, color, instructionSet, horizontalSize, verticalSize):
        self.position = np.array([xPosition, yPosition])
        self.setDirection(direction)        #angle in degrees, 0 = right, clockwise is negative
        self.setStrength(strength)          #Brightness of the light
        self.setSpreadAngle(spreadAngle)    #angle in degrees
        self.setWidth(width)                #Horizontal width of light(mainly for lasers with 0 spread angle)
        self.setColor(color)                #Color of light as a string

        #Choreography instructions setup
        self.instructionIndex = 0
        self.instructionSet = instructionSet
        self.time = 0
        self.halted = False

        #Screen information
        self.horizontalSize = horizontalSize
        self.verticalSize = verticalSize

        self.lightScreen = self.getNewLightScreen()

        self.changed = False
    
    def getNewLightScreen(self):
        self.minVisibleAngle = self.direction - self.spreadAngle / 2
        self.maxVisibleAngle = self.direction + self.spreadAngle / 2
        
        newLightScreen = np.zeros([self.horizontalSize, self.verticalSize, 3])
        
        #Setup edges of light cone boundary
        if self.minVisibleAngle <= -180:
            leftEdge = 0
            leftStep = 0
        else:
            leftEdge = float(self.position[0])
            leftStep = 1 / math.tan(np.deg2rad(self.minVisibleAngle))
        
        if self.maxVisibleAngle >= 0:
            rightEdge = self.horizontalSize
            rightStep = 0
        else:
            rightEdge = float(self.position[0] + self.width)
            rightStep = 1 / math.tan(np.deg2rad(self.maxVisibleAngle))

        #Loop through each row in the screen, setting relevant pixels to be the lights color
        for y in range(self.verticalSize - 1, -1, -1):
            newLightScreen[int(leftEdge):int(rightEdge), y] = self.color
            
            #Update boundaries for next iteration
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
    
    def getMinAngle(self):
        return self.minVisibleAngle
    
    def getMaxAngle(self):
        return self.maxVisibleAngle
    
    def getHorizontalPosition(self):
        return self.position[0]
    
    def getLightScreen(self):
        if self.changed:
            self.lightScreen = self.getNewLightScreen()
        return self.lightScreen
    
    def getWidth(self):
        return self.width
    
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
        self.width = width
        self.changed = True

    def setSpreadAngle(self, spreadAngle):
        self.spreadAngle = spreadAngle
        self.changed = True

    def setStrength(self, strength):
        self.strength = strength
        self.changed = True

    #Update the light to follow the relevant instruction given by choreography
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
                    # print(instruction)
                    self.time = instruction.get("End Time")
            
            elif currentInstruction == "Hold":
                pass
            
            elif currentInstruction == "Stop":
                self.halted = True
            
            elif currentInstruction == "End":
                raise(end)



class smokeMachine:
    def __init__(self, position, strength, direction, speed, instructionSet):
        self.position = np.array(position)
        self.setStrength(strength) #Number of particles spawned
        self.setDirection(direction)
        self.setSpeed(speed)

        #Choreography setup
        self.instructionSet = instructionSet
        self.halted = False
        self.time = 0
        self.instructionIndex = 0
    
    def getNewSmoke(self):
        #Smoke[0] is positions
        #Smoke[1] is velocities
        angleSpread = 15.0 #In degrees the maximum angle off machine direction a particle can be
        speedSpread = 100.0 #The maximum speed off the average a particle can be
        positionSpread = 20 #The maximum distance in each dimension from the machine a particle can spawn

        smokePositions = (np.random.random([self.strength, 2]) - 0.5)  * positionSpread + self.position

        smokeAngles = self.direction + angleSpread * (np.random.random([self.strength]) * 2 - 1)
        smokeSpeeds = self.speed + speedSpread * np.random.random([self.strength])

        smokeVelocities = np.array([np.cos(np.deg2rad(smokeAngles)), np.sin(np.deg2rad(smokeAngles))]) * smokeSpeeds
        smokeVelocities = np.swapaxes(smokeVelocities, 0, 1)

        newSmoke = np.array([smokePositions, smokeVelocities])
        return newSmoke


    def setStrength(self, strength):
        self.strength = int(strength)
    
    def setDirection(self, direction):
        self.direction = direction
    
    def setSpeed(self, speed):
        self.speed = speed
    
    #Update the smoke machine to follow the relevant instruction given by choreography
    def update(self, dt):
        #Instruction Set:Move to, Loop To(Row Index), Hold, Stop, End(Kills whole program)
        if self.halted == False:
            self.time += dt

            instruction = self.instructionSet.iloc[self.instructionIndex]
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

#Handles all the smoke machines and particles
class SmokeScreen:
    def __init__(self, horizontalSize, verticalSize, baseSmoke):
        self.baseSmoke = baseSmoke      #The amount of smoke everywhere
        self.particleSize = 10
        self.smokeMachines = []

        #Screen information
        self.horizontalSize = horizontalSize
        self.verticalSize = verticalSize
        self.smokeScreen = np.zeros([horizontalSize, verticalSize]) + baseSmoke


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

    #The velocity screen is the map of movements that the particles slowly follow
    def getNewVelocityScreen(self):
        rescaleFactor = 80
        #Generate a completely random smaller map
        velocityScreen = np.random.random([int(self.horizontalSize / rescaleFactor), int(self.verticalSize / rescaleFactor), 2])
        
        #Stretch the map out to smoothly interpolate between neighbouring points so particles flow in general patters
        velocityScreen = cv2.resize(velocityScreen, [self.verticalSize, self.horizontalSize])[:, :, :2] * 2 - 1
        velocityScreen *= 200

        return velocityScreen
    
    #Move all the particles and get a new smoke level output
    def updateSmokeScreen(self, dt):
        for smokeMachine in self.smokeMachines:
            smokeMachine.update(dt)
        

        if self.smokeParticlePositions.size != 0:
            #Have the particle slowly lose intensity as it "difuses"
            particleLife = 10.0
            self.smokeParticleIntensities -= dt / particleLife
            
            #if particles exist move particles
            velocityRetention = 0.94    #How much velocity is retained from previous frame
            velocityRandom = 0.005       #How much velocity is randomly generated
            
            self.smokeParticleVelocities *= velocityRetention
            self.smokeParticleVelocities += 20 *  velocityRandom * np.random.normal(size = self.smokeParticleVelocities.shape)

            #Update all velocities based on velocity map
            for i in range(0, len(self.smokeParticlePositions)):
                position = self.smokeParticlePositions[i].astype(int)
                self.smokeParticleVelocities[i] += (1 - velocityRetention -velocityRandom) * self.velocityScreen[position[0], position[1]]
            
            #Move the particles
            self.smokeParticlePositions += self.smokeParticleVelocities * dt

            #Create new particles
            for smokeMachine in self.smokeMachines:
                newSmokeParticles = smokeMachine.getNewSmoke()

                self.smokeParticlePositions = np.append(self.smokeParticlePositions, newSmokeParticles[0], 0)
                self.smokeParticleVelocities = np.append(self.smokeParticleVelocities, newSmokeParticles[1], 0)
                self.smokeParticleIntensities = np.append(self.smokeParticleIntensities, np.ones([newSmokeParticles.shape[1]]))
        else:
            #if no particles exist create new particles
            for smokeMachine in self.smokeMachines:
                newSmokeParticles = smokeMachine.getNewSmoke()

                self.smokeParticlePositions = newSmokeParticles[0]
                self.smokeParticleVelocities = newSmokeParticles[1]
                self.smokeParticleIntensities = np.ones([newSmokeParticles.shape[1]])


        newSmokeScreen = np.zeros([self.horizontalSize + 2 * self.particleSize, self.verticalSize + 2 * self.particleSize]) + self.baseSmoke
        #If there actually are particles(a smoke machine has been created and turned on)
        if self.smokeParticlePositions.size > 0:
            toDelete = [] #List of illegal particles to be removed
            for i in range(0, len(self.smokeParticlePositions)):
                smokeParticlePosition = self.smokeParticlePositions[i]
                if min(smokeParticlePosition) < 0 or smokeParticlePosition[0] > self.horizontalSize or smokeParticlePosition[1] > self.verticalSize or self.smokeParticleIntensities[i] <= 0:
                    #If particle is illegal add it to the list to be deleted
                    toDelete.append(i)
                else:
                    #Set the raw smoke cells
                    endPosition = smokeParticlePosition + self.particleSize
                    newSmokeScreen[int(smokeParticlePosition[0]):int(endPosition[0]), int(smokeParticlePosition[1]):int(endPosition[1])] += self.smokeParticleIntensities[i]

            #Delete illegal particles
            self.smokeParticlePositions = np.delete(self.smokeParticlePositions, toDelete, 0)
            self.smokeParticleVelocities = np.delete(self.smokeParticleVelocities, toDelete, 0)
            self.smokeParticleIntensities = np.delete(self.smokeParticleIntensities, toDelete, 0)

        #Diffuse the smoke with moore neighbourhoods
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
        return self.image[position[1]][position[0]]
    
    def setBackground(self, imageLocation):
        image = None
        
        try:
            image = plt.imread(imageLocation)   #Read the image
            image = image[:,:,:3]               #Remove the alpha value
            image = cv2.resize(image, [self.horizontalSize, self.verticalSize])
            image = image.swapaxes(0, 1)
            self.image = image
        except FileNotFoundError:
            print("File not Found")
        except:
            print("File Invalid")


#Objects are images that can move
class Object:
    def __init__(self, imageLocation, rotation, position, horizontalSize, instructionSet, screenHorizontalSize, screenVerticalSize):
        self.setPosition(position)
        self.horizontalSize = horizontalSize    #Horizontal size of rescaled image
        self.screenHorizontalSize = screenHorizontalSize
        self.screenVerticalSize = screenVerticalSize
        
        #Choreograpy setup
        self.instructionSet = instructionSet
        self.halted = False
        self.time = 0
        self.instructionIndex = 0
        
        try:
            #Load and rotate image
            image = plt.imread(imageLocation)
            image = np.rot90(image, rotation + 2, (0, 1))
            
            #If needed add alpha channel
            if image.shape[2] == 3:
                image = np.append(image, 1.0, 3)
            
            #Rescale image
            self.verticalSize = int(horizontalSize / image.shape[1] * image.shape[0])
            image = cv2.resize(image, [horizontalSize, self.verticalSize])
            self.image = image.swapaxes(0, 1)
        except:
            print("File Invalid")
            self.image = np.zeros([horizontalSize, horizontalSize, 4])
            self.verticalSize = horizontalSize
    
    #Place the object on the screen in its current position and return the screen
    def getObjectScreen(self):
        screen = np.zeros([self.screenHorizontalSize, self.screenVerticalSize, 4])
        
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

        screen[xPos:(xPos + dX), yPos:(yPos + dY)] = self.image[minX:maxX, minY:maxY]
        return screen
    
    def setPosition(self, position):
        self.horizontalPosition = int(position[0])
        self.verticalPosition = int(position[1])
    

    #Update the object to follow the relevant instruction given by choreography
    def update(self, dt):
        #Instruction Set:Move to, Loop To(Row Index), Hold, Stop, End(Kills whole program)
        if self.halted == False:
            self.time += dt

            instruction = self.instructionSet.iloc[self.instructionIndex]
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

#Controls all the things on the stage
class Scene:
    def __init__(self, horizontalSize, verticalSize, baseSmoke):
        self.horizontalSize = horizontalSize
        self.verticalSize = verticalSize

        self.lightList = []
        self.objectList = []

        self.background = Background(horizontalSize, verticalSize)
        self.smoke = SmokeScreen(horizontalSize, verticalSize, baseSmoke)
    
    def addLight(self, xPosition, direction, strength, spreadAngle, width, color, instructionSet):
        self.lightList.append(Light(xPosition, self.verticalSize, direction, strength, spreadAngle, width, color, instructionSet, self.horizontalSize, self.verticalSize))

    def addSmokeMachine(self, position, strength, direction, speed, instructionSet):
        self.smoke.addSmokeMachine(position, strength, direction, speed, instructionSet)
    
    def addObject(self, imageLocation, rotation, position, horizontalSize, instructionSet):
        self.objectList.append(Object(imageLocation, rotation, position, horizontalSize, instructionSet, self.horizontalSize, self.verticalSize))

    #Deals with the top figure that shows the light position, strength, angle and color
    def getLightPatchCollection(self):
        patches = []
        colors = np.array([[]])

        for light in self.lightList:
            newcolor = np.array([light.getColor(), light.getColor()])
            
            #Store the color of the light
            if colors.size == 0:
                colors = newcolor
            else:
                colors = np.append(colors, newcolor, axis=0)
            
            colors = np.clip(colors, 0, 1)
            #Set the shape and position of the light
            position = (light.getHorizontalPosition(), 26)
            minAngle = light.getMinAngle()
            maxAngle = light.getMaxAngle()
            patches.append(Wedge(position, 20, minAngle, maxAngle))
            
            #For lasers create a parralelogram
            p0 = position
            p1 = position + np.array([light.getWidth(), 0])
            down = 20 * np.array([math.cos(np.deg2rad(minAngle)), math.sin(np.deg2rad(minAngle))])
            p2 = p1 + down
            p3 = p0 + down
            patches.append(Polygon(np.array([p0, p1, p2, p3]), closed=True))
        
        #Set the colors of the shapes
        colors *= 0.99
        collection = PatchCollection(patches, alpha=1.0)
        collection.set_facecolors(colors)

        return collection



    def setBackground(self, imageLocation):
        self.background.setBackground(imageLocation)

    #Calculate the frame to be displayed
    #Everything is done in screens, each screen is a 3d numpy array, 2 for pixel location(size of output image) and one for color
    #Light screens are everywhere light is emitted
    #Smoke screen is smoke intensity
    #Object screen is colors of objects
    #Backdrop Screen is the backdrop color    
    def render(self, dt):
        self.smoke.updateSmokeScreen(dt)
        
        #Each light screen is gotten and added elementwise producing an overall lightscreen
        lightScreen = np.zeros([self.horizontalSize, self.verticalSize, 3])
        for light in self.lightList:
            light.update(dt)
            lightScreen += light.getLightScreen()
        
        #Smokescreen is gotten and converted to have same shape as color
        smokeScreen = self.smoke.getSmokeScreen()
        smokeScreen = np.stack([smokeScreen, smokeScreen, smokeScreen], -1)
        
        #Smokescreen is combined with lightscreen to produce a screen with the light on the smoke
        litSmokeScreen = smokeScreen * lightScreen

        #Backdrop is gotten then objects overlayed
        backdrop = self.background.getBackground()
        backdrop = np.fliplr(backdrop)

        for object in self.objectList:
            object.update(dt)
            objectScreen = object.getObjectScreen()
            alphaMask = objectScreen[:, :, 3]
            alphaMask = np.stack([alphaMask, alphaMask, alphaMask], -1)
            objectScreen = objectScreen[:, :, :3]
            backdrop = alphaMask * objectScreen + (1.0 - alphaMask) * backdrop

        #Backdrop is combined with light not absorbed by smoke to produce a screen with light on the backdrop and objects
        litBackdrop = lightScreen * backdrop * (1 - smokeScreen)

        #Lit smoke and lit backdrop are combined to fnd total 
        output = litSmokeScreen + litBackdrop

        #Rescale the output as when multiple lights are overlayed they can exceed brightness able to be shown, so entire image brightness is reduced
        output /= max(1, output.max())

        #Re-orient to work with matplotlib
        output = np.swapaxes(output, 0, 1)

        return output
    
