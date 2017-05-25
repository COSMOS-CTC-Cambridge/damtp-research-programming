plotfilename="../files/matplotlib-3d-example.png"
import sys
import Game_of_Life

import matplotlib
import matplotlib.pyplot
import matplotlib.animation

matplotlib.pyplot.ion()

def frame_generator(iteration, state, fig, ax, state_updater):
    state[:] = state_updater(state)[:]
    axesimage = ax.imshow(state)
    return [axesimage]

def animate_game(size=(100,100)):
    fig = matplotlib.pyplot.figure()
    ax = fig.add_subplot(111)
    state = Game_of_Life.initial(size)
    ani = matplotlib.animation.FuncAnimation(fig, frame_generator, fargs=(state, fig, ax, Game_of_Life.step),
                                             blit=False, interval=10, frames=10,
                                             repeat=True)
    matplotlib.pyplot.show()
    return ani
