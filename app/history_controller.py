import threading
import config
import csv
import history_data as hd
import os
import datetime
import queue
from plotter import *


class HistoryController(threading.Thread):

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self._queue = queue
        self._registered_ids = {}
        self._plotter = None

        for t in hd.HistoryDataType:
            self._registered_ids[t] = []

        if not config.HISTORY_DIR.endswith('/'):
            self._file_dir = config.HISTORY_DIR + '/' + str(datetime.date.today()) + '/'
        else:
            self._file_dir = config.HISTORY_DIR + str(datetime.date.today()) + '/'

    def run(self):
        print("Starting History Controller")
        if not self.create_directory():
            return

        if config.PLOT_BPM:
            self._plotter = Plotter(hd.HistoryDataType.BPM, self._file_dir)
        elif config.PLOT_RR:
            self._plotter = Plotter(hd.HistoryDataType.RR, self._file_dir)

        if self._plotter:
            self._plotter.start()

        while not self._stop_event.is_set():
            try:
                data = self._queue.get(timeout=1)
                self.log_data(data)
            except queue.Empty:
                pass

    def create_directory(self):

        try:
            if not os.path.isdir(self._file_dir):
                os.makedirs(self._file_dir)
        except OSError:
            print("Could not create directory at %s - history controller is shutting down..." % self._file_dir)
            return False

        subdir = sum(os.path.isdir(os.path.join(self._file_dir, i)) for i in os.listdir(self._file_dir)) + 1
        # avoid overwriting csvs in case some subfolders were deleted
        while os.path.isdir(self._file_dir + str(subdir)):
            subdir = subdir + 1
        self._file_dir = self._file_dir + str(subdir) + '/'

        try:
            os.mkdir(self._file_dir)
            return True
        except OSError:
            print("Could not subdirectory at %s - history controller is shutting down..." % self._file_dir)
            return False

    def log_data(self, data):
        if data.get_id() not in self._registered_ids[data.get_type()]:
            self._registered_ids[data.get_type()].append(data.get_id())

        csv_file = open(self._file_dir + data.get_type().name + '_' + str(data.get_id()) + ".csv", "a")
        writer = csv.writer(csv_file,
                            delimiter=",",
                            quotechar='"',
                            quoting=csv.QUOTE_MINIMAL)

        writer.writerow([data.get_data()])
        csv_file.flush()
        csv_file.close()

    def stop(self):
        self._stop_event.set()
        self._plotter.stop()

    def get_queue(self):
        return self._queue
