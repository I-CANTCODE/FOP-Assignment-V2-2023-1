import matplotlib.pyplot as plt
import sceneElements as SE
import time
import pandas

#Create custom errors for loading choreography
class failedStageInit(Exception):
    pass
class missingValue(Exception):
    def __init__(self, type, rowIndex):
        print("Recquired value is missing from input file for " + type + " in row " + str(2 + rowIndex))



try:
    #Load the choreography file and get the initialisation sheet
    choreogrpahy = pandas.read_excel("Choreography.xlsx", None)
    init = choreogrpahy['init']

    #Check recquired values are present then initialise stage
    if init.get("Type").get(1) != "Stage":
        raise failedStageInit
    
    isNull = init.loc[1].isna().to_list()
    if True in isNull[1:4]:
        raise missingValue("stage", 1)
    
    horizontalSize = init.get('a').get(1)
    verticalSize = init.get('b').get(1)
    baseSmoke = init.get('c').get(1)

    stage = SE.Scene(horizontalSize, verticalSize, baseSmoke)
    
    if isNull[4] == False:
        stage.setBackground(init.get('d').get(1))



    #Go through each row in initialisation sheet and create all the recquired objects, checking recquired values are present
    for rowIndex in range(0, len(init.index)):
        row = init.iloc[rowIndex]

        #Create Lights
        if row.get("Type") == "Light":
            rowNulls = row.isna().to_list()
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
        
        #Create Smoke Machines
        elif row.get("Type") == "Smoke Machine":
            rowNulls = row.isna().to_list()
            if True in rowNulls[1:6]:
                raise missingValue("smokeMachine", rowIndex)
            
            position = [row.get('b'), row.get('c')]
            strength = row.get('d')
            direction = row.get('e')
            speed = row.get('f')
            
            instructionSet = choreogrpahy[row.get('a')]
            stage.addSmokeMachine(position, strength, direction, speed, instructionSet)
        
        #Create objects(images on the stage)
        elif row.get("Type") == "Object":
            rowNulls = row.isna().to_list()
            if True in rowNulls[1:6]:
                raise missingValue("smokeMachine", rowIndex)
            
            imageLocation = row.get('b')
            position = [row.get('c'), row.get('d')]
            horizontalSize = row.get('e')
            rotation = row.get('f')
            
            instructionSet = choreogrpahy[row.get('a')]
            stage.addObject(imageLocation, rotation, position, horizontalSize, instructionSet)
    
    
    #Setup rendering loop and render first frame
    dt = 0
    fig, axs = plt.subplots(nrows = 2, ncols = 1, figsize = (6, 6), gridspec_kw={'height_ratios': [1, 6]})
    axs[1] = plt.imshow(stage.render(0), origin='lower')
    plt.draw()
    plt.pause(0.0001)

    #Main render Loop
    for i in range(10000):
        startTime = time.monotonic()

        axs[1].set_data(stage.render(dt))

        #Setup light plot
        axs[0].cla()
        axs[0].set_xlim([0, 512])
        axs[0].set_ylim([0, 32])
        axs[0].set_facecolor('k')
        axs[0].add_collection(stage.getLightPatchCollection())
        
        plt.draw()
        plt.pause(0.0001)

        lastTime = time.monotonic()
        dt =  lastTime - startTime
        # print("FPS: " + str(1 / dt))


except failedStageInit:
    print("Stage init failed")
except missingValue:
    pass
except FileNotFoundError:
    print("Choreography file was not found")
except SE.end:
    pass

