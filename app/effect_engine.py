import threading
import config


class EffectEngine(threading.Thread):

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self._queue = queue
        self._currentBpm = 0
        self._heartbeat = config.HEARTBEAT_TIMEOUT
        self._name = ""
        self._bpmHistory = list()
        self._stop_event = threading.Event()

    def set_bpm(self, bpm):
        self._currentBpm = bpm

    def stop(self):
        self._stop_event.set()

    def get_queue(self):
        return self._queue

    def get_name(self):
        return self._name

    def stop(self):
        self._stop_event.set()
