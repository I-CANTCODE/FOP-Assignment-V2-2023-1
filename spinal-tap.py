import matplotlib.pyplot as plt
import sceneElements as SE
import time

fps = 5

startTime = time.monotonic()

stage = SE.Scene(512, 288, 0.1)
stage.setBackground("backdrop.png")
stage.addLight(400, -90, 10, 45, "red")
stage.addLight(256, -90, 11, 90, "blue")
stage.addLight(320, -70, 11, 80, "green")
stage.addSmokeMachine([250, 100], 20, 11)
stage.addObject("drum.png", 0, 200, 5, 150)
stage.addObject("guitar.png", 1, 350, 5, 50)
# plt.imshow(stage.objectList[0].getObjectScreen())
# plt.show()
# print(time.monotonic() - startTime)

frames = []


firstRun = True
frameCount = 10
lastFrameTime = .75
for i in range(0, frameCount):
    print("Rendering frame " + str(i + 1) + " of " + str(frameCount) + ". Time Remaining = " + str((frameCount - i) * lastFrameTime)[:4] + "s")
    frameStartTime = time.monotonic()
    frame = stage.render()
    frames.append(frame)
    lastFrameTime = time.monotonic() - frameStartTime



firstRun = True
for i in range(0, len(frames)):
    # image = None
    if firstRun:
        image = plt.imshow(frames[i], origin="lower")
    else:
        image.set_data(frames[i])
    
    plt.draw()
    plt.pause(1 / fps)

plt.pause(1000000)

# image = plt.imshow(stage.background.image)
# plt.show()
