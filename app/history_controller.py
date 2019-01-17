import threading
import config
import csv
import history_data
import os
import datetime
import queue

class HistoryController(threading.Thread):

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self._queue = queue
        if not config.HISTORY_DIR.endswith('/'):
            self._file_dir = config.HISTORY_DIR + '/' + str(datetime.date.today()) + '/'
        else:
            self._file_dir = config.HISTORY_DIR + str(datetime.date.today()) + '/'

    def run(self):
        print("Starting History Controller")
        if not self.create_directory():
            return

        while not self._stop_event.is_set():
            try:
                data = self._queue.get_nowait()

            except queue.Empty:
                pass

    def create_directory(self):
        if os.path.isdir(self._file_dir):
            print(os.listdir(self._file_dir))
            subdirs = sum(os.path.isdir(os.path.join(self._file_dir, i)) for i in os.listdir(self._file_dir))
            print(subdirs)
            self._file_dir = self._file_dir + str(subdirs + 1)
        else:
            self._file_dir = self._file_dir + "1"
        try:
            os.makedirs(self._file_dir)
            return True

        except OSError:
            print("Could not create directory at %s - history controller is shutting down..." % self._file_dir)
            return False
