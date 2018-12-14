from effect_engine import EffectEngine
import config
import pyaudio
import wave
import time
import queue
import csv


class SoundEffectEngine(EffectEngine):

    def __init__(self, queue):
        super().__init__(queue)
        self._name = "SoundEffectEngine"
        self._chunk = 1024
        self._player = pyaudio.PyAudio()
        self._wav_file_path = config.SOUNDFILE_PATH
        self._wav_file = None
        self._stream = None
        self._dataFile = open("history.csv", "w")
        self._dataWriter = csv.writer(
            self._dataFile,
            delimiter=",",
            quotechar='"',
            quoting=csv.QUOTE_MINIMAL)

    def run(self):
        print("Starting " + self._name)
        self._wav_file = wave.open(self._wav_file_path, "rb")
        self._stream = self._player.open(
            format=self._player.get_format_from_width(
                self._wav_file.getsampwidth()),
            channels=self._wav_file.getnchannels(),
            rate=self._wav_file.getframerate(),
            output=True)
        self.effect_loop()

    def idle(self):
        print(self._name + " idling..")
        self._stream.stop_stream()
        bpm = self._queue.get()
        self._currentBpm = bpm if bpm > 0 else self._currentBpm
        print("Received bpm from dispatcher: " + str(self._currentBpm))
        self._stream.start_stream()
        self._heartbeat = config.HEARTBEAT_TIMEOUT

    def effect_loop(self):

        try:
            while True:

                data = self._wav_file.readframes(self._chunk)
                while data != b'':
                    self._stream.write(data)
                    data = self._wav_file.readframes(self._chunk)

                self._wav_file.rewind()
                print("Rewind")
                try:
                    bpm = self._queue.get_nowait()
                    self._heartbeat = config.HEARTBEAT_TIMEOUT
                    self._currentBpm = bpm if bpm > 0 else self._currentBpm
                    print("Received bpm from dispatcher: " + str(
                            self._currentBpm))
                    # save data history
                    if self._currentBpm != 0:
                        self._bpmHistory.append(self._currentBpm)
                        # write into csv

                        self._dataWriter.writerow([self._currentBpm])
                        self._dataFile.flush()
                except queue.Empty:
                    self._heartbeat = self._heartbeat - 1

                if self._heartbeat is 0:
                    self.idle()
                else:
                    if self._currentBpm is 0:
                        time.sleep(1)
                    else:
                        # adjust pause between heartbeats
                        time.sleep(60/self._currentBpm)
        except KeyboardInterrupt:
            print("Got interrupt, crunching Data...")
