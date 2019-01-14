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
from natsort import natsorted
from ring_buffer import RingBuffer


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
        self._currentBpms = RingBuffer(config.AVG_WINDOW)
        self._heartbeat = config.HEARTBEAT_TIMEOUT

        if config.BPM_RANGE_LOW >= config.BPM_RANGE_HIGH:
            raise ValueError("BPM Ranges are not configured correctly in config")

    def read_wav_files(self):
        self._wav_files = [join(self._wav_dir, f) for f in listdir(self._wav_dir) if isfile(join(self._wav_dir, f))]
        self._wav_files = natsorted(self._wav_files, key=lambda y: y.lower())
        if len(self._wav_files) < 1:
            raise FileNotFoundError("No wav files found in given directory.")

    def run(self):
        print("Starting " + self._name)
        self.read_wav_files()
        self.effect_loop()

    def shutdown_audio(self):
        self._cur_wav_file.close()
        self._stream.stop_stream()
        try:
            self._player.close(self._stream)
        except ValueError:
            pass

    def idle(self):
        print(self._name + " idling..")
        self.shutdown_audio()
        self._currentBpms.reset()
        while not self._stop_event.is_set():
            try:
                bpm = self._queue.get(timeout=2)
                if bpm > 0:
                    self._currentBpms.append(bpm)
                print("Received bpm from dispatcher: " + str(bpm))
                self.open_wav_file()
                self._heartbeat = config.HEARTBEAT_TIMEOUT
                break
            except queue.Empty:
                pass

    def poll_bpm(self):
        try:
            bpm = self._queue.get_nowait()
            self._heartbeat = config.HEARTBEAT_TIMEOUT
            if bpm > 0:
                self._currentBpms.append(bpm)
                self._bpmHistory.append(bpm)
                # write into csv
                self._dataWriter.writerow([bpm])
                self._dataFile.flush()
            print("Received bpm from dispatcher: " + str(bpm))
            # save data history

        except queue.Empty:
            self._heartbeat = self._heartbeat - 1

    def open_wav_file(self):
        index = self.choose_wav_file()
        self._cur_wav_file = wave.open(self._wav_files[index], "rb")
        self._stream = self._player.open(
            format=self._player.get_format_from_width(
                self._cur_wav_file.getsampwidth()),
            channels=self._cur_wav_file.getnchannels(),
            rate=self._cur_wav_file.getframerate(),
            output=True)

    def choose_wav_file(self):
        if self._currentBpms.get_len() is 0:
            return 0

        if config.SOUND_MODE is config.SoundMode.AVERAGE:
            bpm = self._currentBpms.get_sum() / self._currentBpms.get_len()

            limited_bpm = config.BPM_RANGE_LOW if bpm < config.BPM_RANGE_LOW else \
                config.BPM_RANGE_HIGH if bpm > config.BPM_RANGE_HIGH else bpm
            total_range = config.BPM_RANGE_HIGH - config.BPM_RANGE_LOW
            index = math.floor((limited_bpm - config.BPM_RANGE_LOW) / math.ceil(total_range/len(self._wav_files)))

        print(index)
        return index

    def effect_loop(self):

        self.poll_bpm()
        self.open_wav_file()

        try:
            while True:

                if self._stop_event.is_set():
                    self.shutdown_audio()
                    return

                data = self._cur_wav_file.readframes(self._chunk)
                while data != b'':
                    self._stream.write(data)
                    data = self._cur_wav_file.readframes(self._chunk)

                self.poll_bpm()
                if self._heartbeat is 0:
                    self.idle()
                else:
                    self.shutdown_audio()
                    self.open_wav_file()

                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Got interrupt, crunching Data...")
