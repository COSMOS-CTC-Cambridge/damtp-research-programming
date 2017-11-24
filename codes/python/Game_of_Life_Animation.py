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

def animate_game(state_initialiser, state_updater, **kwargs):
    fig = matplotlib.pyplot.figure()
    state = state_initialiser(**kwargs)
    while True:
        matplotlib.pyplot.imshow(state)
        #plt.show()
        matplotlib.pyplot.pause(.1)
        matplotlib.pyplot.draw()    
        matplotlib.pyplot.clf()
        state = state_updater(state)

animate_game(state_initialiser=Game_of_Life.initial, state_updater=Game_of_Life.step, size=(10,10))
