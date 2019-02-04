import os
from numpy import genfromtxt
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.animation as animation
import threading
import config

class Plotter(threading.Thread):

    def __init__(self, type, path):
        threading.Thread.__init__(self)
        self._type = type
        self._path = path
        self._GRAPH_OFFSET = 40.
        self._ALPHA_FACTOR = 0.1
        self._data = {}

    def run(self):
        matplotlib.rcParams['toolbar'] = 'None'
        self._fig = plt.figure()
        self._ax = self._fig.add_subplot(1,1,1)
        self._fig.patch.set_facecolor('black')
        plt.axis('off')
        self._fig.tight_layout()
        figManager = plt.get_current_fig_manager()
        figManager.full_screen_toggle()

        ani = animation.FuncAnimation(self._fig, self.plot, interval=config.PLOT_INTERVAL)
        plt.show()

    def plot(self,i):
        i = 0
        for f in self.collect_files():
            try:
                my_data = genfromtxt(f, delimiter=',')
                my_data = my_data + i * self._GRAPH_OFFSET
                self._ax.plot(my_data, color="white", alpha=1 - (self._ALPHA_FACTOR * i))
                i = i + 1
            except IndexError:
                pass

    def collect_files(self):
        # collect all csv file paths of the respective data type
        return [os.path.join(self._path, f) for f in os.listdir(self._path) if ".csv" in f and self._type.name in f]

