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
        self._registered_ids = {}

        for t in history_data.HistoryDataType:
            self._registered_ids[t] = []

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
                self.log_data(data)

            except queue.Empty:
                pass

    def create_directory(self):
        if os.path.isdir(self._file_dir):
            subdirs = sum(os.path.isdir(os.path.join(self._file_dir, i)) for i in os.listdir(self._file_dir))
            self._file_dir = self._file_dir + str(subdirs + 1) + '/'
        else:
            self._file_dir = self._file_dir + "1" + '/'
        try:
            os.makedirs(self._file_dir)
            return True

        except OSError:
            print("Could not create directory at %s - history controller is shutting down..." % self._file_dir)
            return False

    def log_data(self, data):
        if data.get_id() not in self._registered_ids[data.get_type()]:
            self._registered_ids[data.get_type()].append(data.get_id())

        csvFile = open(self._file_dir + data.get_type().name + '_' + str(data.get_id()) + ".csv", "w")
        writer = csv.writer(csvFile,
                            delimiter=",",
                            quotechar='"',
                            quoting=csv.QUOTE_MINIMAL)

        writer.writerow([data.get_data()])
        writer.flush()
        csvFile.close()

    def stop(self):
        self._stop_event.set()

    def get_queue(self):
        return self._queue
