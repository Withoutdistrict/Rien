import matplotlib.pyplot as plt
import matplotlib.animation as animation

colors = ["Red", "violet", "DarkOrange", "Yellow", "Magenta", "Purple", "Lime", "Green", "Teal", "Cyan", "DarkBlue", "Maroon", "Black"]

def animate(i):
    rect.set_xy((i,i))
    rect.set_facecolor(colors[i%12])
    rect.set_visible(True)
    return rect,

fig = plt.figure(figsize = (5,5))
ax = plt.axes(xlim=(0,100), ylim=(0,100), aspect='equal')
rect = plt.Rectangle((70,20), 10, 10, fill=True, color='gold', ec='blue')
ax.add_patch(rect)

anim = animation.FuncAnimation(fig, animate, frames=91,interval=20, blit=False, repeat=True)

plt.show()