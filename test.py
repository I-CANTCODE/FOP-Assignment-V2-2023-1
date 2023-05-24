import numpy as np
import matplotlib.pyplot as plt
import time
import sceneElements as se
import cv2
import pandas

smoke = se.SmokeScreen(288, 512, 0)
velocity = smoke.getNewVelocityScreen()
velocity = np.swapaxes(velocity, 0, 2)
velocity = velocity[0]
velocity = np.swapaxes(velocity, 0, 1)
plt.imshow(velocity)
plt.colorbar()
plt.show()
# df = pandas.read_excel("Choreography.xlsx", "Light1")
# print(df)
# print(df.get(1))


# plt.imshow(se.SmokeScreen(500, 500, 0).velocityScreen[:, :, 0])
# plt.draw()
# for i in range(0, 10):
#     plt.imshow(se.SmokeScreen(500, 500, 0).velocityScreen[:, :, 0])
#     plt.draw()
#     plt.pause(1)


# array = np.zeros([2, 2])
# array[0, 0] = 1.0
# array = cv2.blur(array, [2, 2])
# print(array)


# array1 = np.array([[0, 1],[2,3]])
# array2 = np.array([[4], [5]])
# array3 = np.array([[], []])
# print(np.concatenate([array3, array1], axis = 1))




# velocityMap = np.zeros([500, 500, 3])
# image = plt.imshow(velocityMap)

# for i in range(0, 10):
#     start = time.monotonic()
#     velocityMap[200] = np.ones([500, 3])
#     velocityMap += 0.1 * np.stack([np.random.rand(500, 500),np.random.rand(500, 500), np.zeros([500, 500])], axis=-1)
#     velocityMap = cv2.blur(velocityMap, [10, 10])
#     print(time.monotonic() - start)

#     image.set_data(velocityMap)
#     plt.draw()
#     plt.pause(1)


# myLight = se.Light(200, 288, -90, 11, 180, "red", 512, 288)
# lightScreen = myLight.lightScreen
# output = np.zeros([288, 512, 3])
# for x in range(0, 512):
#     for y in range(0, 288):
#         output[y][x] = lightScreen[x][y]
# image = plt.imshow(output, origin="lower")
# plt.show()
# test = np.array([range(0, 5), range(0, 5), range(0, 5)])

# print(test[0, 1])


# for j in range(0,3):
#     img = np.random.normal(size=(100,150))
#     plt.figure(1); plt.clf()
#     plt.imshow(img)
#     plt.title('Number ' + str(j))
#     plt.pause(3)

# v1 = np.random.normal(size=(100000,100))
# v2 = np.random.normal(size=(100000,100))
# start = time.monotonic()

# out = v1 + v2

# mid = time.monotonic()

# for x in range(0, 100000):
#     for y in range(0, 100):
#         out = v1[x][y] + v2[x][y]

# end = time.monotonic()

# print(mid - start)
# print(end - mid)