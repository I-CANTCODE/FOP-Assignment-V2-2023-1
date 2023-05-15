import matplotlib.pyplot as plt

fig, (ax0, ax1) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [1, 10]},
                              figsize = (10,10))

ax0.set_aspect("equal")
ax0.fill([0,500,500,0],[0,0,50,50], color="black")
circle1 = plt.Circle([250,25],20, color="red")
ax0.add_patch(circle1)
circle1 = plt.Circle([350,25],20, color="blue")
ax0.add_patch(circle1)

ax1.set_aspect("equal")
ax1.fill([0,500,500,0],[0,0,500,500], color="black")
ax1.fill([230,270,270,230],[490,490,500,500], color="red")
ax1.fill([230,270,330,170],[490,490,0,0], color="red")
ax1.fill([330,370,370,330],[490,490,500,500], color="blue")
ax1.fill([330,370,430,270],[490,490,0,0], color="blue")

plt.suptitle("STAGEVIEW", fontsize="18")
plt.show()


