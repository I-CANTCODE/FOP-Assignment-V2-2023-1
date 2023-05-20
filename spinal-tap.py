import matplotlib.pyplot as plt
import sceneElements as SE
import time
import pandas
import math

class failedStageInit(Exception):
    pass
class missingValue(Exception):
    def __init__(self, type, rowIndex):
        print("Recquired value is missing from input file for " + type + " in row " + str(2 + rowIndex))

fps = 12

startTime = time.monotonic()

try:
    choreogrpahy = pandas.read_excel("Choreography.xlsx", None)
    init = choreogrpahy['init']

    if init.get("Type").get(1) != "Stage":
        raise failedStageInit
    # print(init)
    isNull = init.loc[1].isna().to_list()
    # print(isNull)
    if True in isNull[1:4]:
        raise missingValue("stage", 1)
    horizontalSize = init.get('a').get(1)
    verticalSize = init.get('b').get(1)
    baseSmoke = init.get('c').get(1)

    stage = SE.Scene(horizontalSize, verticalSize, baseSmoke)
    
    if isNull[4] == False:
        stage.setBackground(init.get('d').get(1))

    # if init.iloc(1):

    for rowIndex in range(0, len(init.index)):
        row = init.iloc[rowIndex]
        # print(row)
        if row.get("Type") == "Light":
            rowNulls = row.isna().to_list()
            # print(rowNulls)
            if True in rowNulls[1:]:
                raise missingValue("light", rowIndex)
            horizontalPosition = row.get('b')
            direction = row.get('c')
            strength = row.get('d')
            spreadAngle = row.get('e')
            width = row.get('f')
            color = row.get('g')
            instructionSet = choreogrpahy[row.get('a')]
            stage.addLight(horizontalPosition, direction, strength, spreadAngle, width, color, instructionSet)
        
        
        elif row.get("Type") == "Smoke Machine":
            rowNulls = row.isna().to_list()
            # print(rowNulls)
            if True in rowNulls[1:6]:
                raise missingValue("smokeMachine", rowIndex)
            position = [row.get('b'), row.get('c')]
            strength = row.get('d')
            direction = row.get('e')
            speed = row.get('f')
            instructionSet = choreogrpahy[row.get('a')]
            stage.addSmokeMachine(position, strength, direction, speed, instructionSet)
        
        
        elif row.get("Type") == "Object":
            rowNulls = row.isna().to_list()
            # print(rowNulls)
            if True in rowNulls[1:6]:
                raise missingValue("smokeMachine", rowIndex)
            imageLocation = row.get('b')
            position = [row.get('c'), row.get('d')]
            horizontalSize = row.get('e')
            rotation = row.get('f')
            instructionSet = choreogrpahy[row.get('a')]
            stage.addObject(imageLocation, rotation, position, horizontalSize, instructionSet)
    
    
    firstRun = True
    dt = 0
    image = plt.imshow(stage.render(0), origin='lower')
    plt.draw()
    for i in range(10000):
        startTime = time.monotonic()
        image.set_data(stage.render(dt))
        plt.draw()
        plt.pause(0.0001)
        lastTime = time.monotonic()
        dt =  lastTime - startTime
        # print("FPS: " + str(1 / (lastTime - startTime)))
except failedStageInit:
    print("Stage init failed")
except missingValue:
    pass
except FileNotFoundError:
    print("Choreography file was not found")
except SE.end:
    pass

# stage = SE.Scene(512, 288, 0)
# stage.setBackground("backdrop.png")
# stage.addLight(400, -90, 10, 45, 0, "red")
# stage.addLight(256, -90, 11, 90, 0, "blue")
# stage.addLight(320, -70, 8, 0, 10, "green")
# stage.addLight(256, -90, 3, 180, 0, "white")
# stage.addSmokeMachine([100, 50], 5, 30, 200)
# stage.addObject("drum.png", 0, [200, 5], 150)
# stage.addObject("guitar.png", 1, [350, 5], 50)
# plt.imshow(stage.objectList[0].getObjectScreen())
# plt.show()
# print(time.monotonic() - startTime)


