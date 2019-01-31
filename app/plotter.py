import os
from numpy import genfromtxt
import matplotlib.pyplot as plt;
import matplotlib
import history_data as hd
import config


class Plotter:

    def __init__(self, type, path):
        self._type = type
        self._path = path
        self._GRAPH_OFFSET = 40.
        self._ALPHA_FACTOR = 0.1

    def plot(self):
        if self._type is hd.HistoryDataType.BPM:
            self.plot_bpm()

    def plot_bpm(self):
        matplotlib.rcParams['toolbar'] = 'None'
        fig = plt.figure()
        fig.patch.set_facecolor('black')
        plt.axis('off')

        i = 0
        for f in self.collect_files():
            try:
                my_data = genfromtxt(f, delimiter=',')
                my_data = my_data + i * self._GRAPH_OFFSET
                plt.plot(my_data, color="white", alpha=1 - (self._ALPHA_FACTOR * i))
                i = i + 1
            except IndexError:
                pass

        figManager = plt.get_current_fig_manager()
        figManager.full_screen_toggle()
        plt.show()

    def collect_files(self):
        # collect all csv file paths of the repective data type
        return [os.path.join(self._path, f) for f in os.listdir(self._path) if ".csv" in f and self._type.name in f]

