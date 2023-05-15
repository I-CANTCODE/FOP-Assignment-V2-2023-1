import matplotlib.pyplot as plt
import sceneElements as SE
import time

fps = 5

startTime = time.monotonic()

stage = SE.scene(512, 288, 0.1)
stage.setBackground("Assignment V2/backdrop.png")
stage.addLight(400, -90, 10, 45, "red")
stage.addLight(256, -90, 11, 90, "blue")
stage.addLight(320, -70, 11, 80, "green")
stage.addSmokeMachine([250, 100], 20, 11)
print(time.monotonic() - startTime)

frames = []


firstRun = True
frameCount = 1
for i in range(0, frameCount):
    frameStartTime = time.monotonic()
    print("Rendering frame " + str(i + 1) + " of " + str(frameCount))
    image = stage.render()
    frames.append(image)
    print(time.monotonic() - frameStartTime)



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