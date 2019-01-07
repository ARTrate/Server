from effect_engine import EffectEngine
import config
import pyaudio
import wave
import time
import queue
import csv
from os import listdir
from os.path import isfile, join
import math
from natsort import natsorted, ns


class SoundEffectEngine(EffectEngine):

    def __init__(self, queue):
        super().__init__(queue)
        self._name = "SoundEffectEngine"
        self._chunk = 1024
        self._player = pyaudio.PyAudio()
        self._wav_dir = config.SOUNDFILE_DIR
        self._wav_files = {}
        self._cur_wav_file = None
        self._stream = None
        self._dataFile = open("history.csv", "w")
        self._dataWriter = csv.writer(
            self._dataFile,
            delimiter=",",
            quotechar='"',
            quoting=csv.QUOTE_MINIMAL)
        self._currentBpm = 0
        self._heartbeat = config.HEARTBEAT_TIMEOUT

    def read_wav_files(self):
        self._wav_files = [join(self._wav_dir, f) for f in listdir(self._wav_dir) if isfile(join(self._wav_dir, f))]
        self._wav_files = natsorted(self._wav_files, key=lambda y: y.lower())
        print(self._wav_files)

    def run(self):
        print("Starting " + self._name)
        self.read_wav_files()
        self.effect_loop()

    def shutdownAudio(self):
        self._cur_wav_file.close()
        self._stream.stop_stream()
        self._player.close(self._stream)

    def idle(self):
        print(self._name + " idling..")
        self.shutdownAudio()
        while not self._stop_event.is_set():
            try:
                bpm = self._queue.get(timeout=2)
                self._currentBpm = bpm if bpm > 0 else self._currentBpm
                print("Received bpm from dispatcher: " + str(self._currentBpm))
                self._stream.start_stream()
                self._heartbeat = config.HEARTBEAT_TIMEOUT
            except queue.Empty:
                pass

    def poll_bpm(self):
        try:
            bpm = self._queue.get_nowait()
            self._heartbeat = config.HEARTBEAT_TIMEOUT
            bpm_old = self._currentBpm
            self._currentBpm = bpm if bpm > 0 else self._currentBpm
            print("Received bpm from dispatcher: " + str(self._currentBpm))
            # save data history
            if self._currentBpm != 0:
                self._bpmHistory.append(self._currentBpm)
                # write into csv

                self._dataWriter.writerow([self._currentBpm])
                self._dataFile.flush()
            if bpm_old != self._currentBpm:
                return True
            else:
                return False
        except queue.Empty:
            self._heartbeat = self._heartbeat - 1
            return False

    def choose_wav_file(self):
        limited_bpm = config.BPM_RANGE_LOW if self._currentBpm < config.BPM_RANGE_LOW else \
            config.BPM_RANGE_HIGH if self._currentBpm > config.BPM_RANGE_HIGH else self._currentBpm
        total_range = config.BPM_RANGE_HIGH - config.BPM_RANGE_LOW
        index = math.floor((limited_bpm - config.BPM_RANGE_LOW)/math.floor(total_range/len(self._wav_files)))
        print(index)
        self._cur_wav_file = wave.open(self._wav_files[index], "rb")
        self._stream = self._player.open(
            format=self._player.get_format_from_width(
                self._cur_wav_file.getsampwidth()),
            channels=self._cur_wav_file.getnchannels(),
            rate=self._cur_wav_file.getframerate(),
            output=True)

    def effect_loop(self):

        self.poll_bpm()
        self.choose_wav_file()

        try:
            while True:

                if self._stop_event.is_set():
                    self.shutdownAudio()
                    return

                data = self._cur_wav_file.readframes(self._chunk)
                while data != b'':
                    self._stream.write(data)
                    data = self._cur_wav_file.readframes(self._chunk)

                changed = self.poll_bpm()
                if self._heartbeat is 0:
                    self.idle()
                elif changed:
                    self.shutdownAudio()
                    self.choose_wav_file()
                else:
                    self._cur_wav_file.rewind()

                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Got interrupt, crunching Data...")
