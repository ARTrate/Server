import os
from numpy import genfromtxt
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.animation as animation
import threading
import config
from collections import deque
import history_data as hd
import math

RR_COLORS = ["aquamarine","turquoise", "darkturquoise","c","teal","darkslategrey"]
RR_MIN = 10
RR_MAX = 22


class Plotter(threading.Thread):

    def __init__(self, type, path):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self._type = type
        self._path = path
        self._GRAPH_OFFSET = 40.
        self._ALPHA_FACTOR = 0.1
        self._data = {}
        self._fig = None
        self._ax = None
        self._ani = None

    def run(self):
        matplotlib.rcParams['toolbar'] = 'None'
        self._fig = plt.figure()
        self._ax = self._fig.add_subplot(1,1,1)
        self._fig.patch.set_facecolor(RR_COLORS[0])
        plt.axis('off')
        self._fig.tight_layout()
        fig_manager = plt.get_current_fig_manager()
        fig_manager.full_screen_toggle()

        self._ani = animation.FuncAnimation(self._fig, self.plot, interval=config.PLOT_INTERVAL)
        plt.show()

    def stop(self):
        self._stop_event.set()

    def plot(self, i):
        if self._stop_event.is_set():
            self._ani.event_source.stop()
            plt.close("all")
            return

        del self._ax.lines[:]  # prevent overdrawing the lines to preserve varying alpha

        i = 0
        for csv in self.collect_files(self._type.name):
            try:
                with open(csv, 'r') as f:
                    lines = deque(f, config.PLOT_WINDOW)
                    my_data = genfromtxt(lines, delimiter=',')
                    my_data = my_data + i * self._GRAPH_OFFSET
                    self._ax.plot(my_data, color="white", alpha=1 - (self._ALPHA_FACTOR * i))
                i = i + 1
            except IndexError:
                pass

        for csv in self.collect_files(hd.HistoryDataType.RR.name):
            try:
                with open(csv, 'r') as f:
                    lines = deque(f, 1)
                    my_data = genfromtxt(lines, delimiter=',')
                    total_range = RR_MAX - RR_MIN
                    if my_data > RR_MAX:
                        my_data = RR_MAX
                    elif my_data < RR_MIN:
                        my_data = RR_MIN
                    index = math.floor((my_data - RR_MIN) / math.ceil(total_range / len(RR_COLORS)))
                    self._fig.patch.set_facecolor(RR_COLORS[index])
            except IndexError:
                pass

    def collect_files(self, type):
        # collect all csv file paths of the respective data type
        return [os.path.join(self._path, f) for f in os.listdir(self._path) if ".csv" in f and type in f]
