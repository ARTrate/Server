from effect_engine import *
import pyaudio
import wave
import time
import queue

class SoundEffectEngine(EffectEngine):

    def __init__(self, queue):
        super().__init__(queue)
        self._name = "SoundEffectEngine"
        self._chunk = 1024
        self._player = pyaudio.PyAudio()
        self._wav_file_path = "media/351.wav"  # @TODO: make configurable
        self._wav_file = None
        self._stream = None

    def run(self):
        print("Starting " + self._name)
        self._wav_file = wave.open(self._wav_file_path, "rb")
        self._stream = self._player.open(format=self._player.get_format_from_width(self._wav_file.getsampwidth()),
                                         channels=self._wav_file.getnchannels(),
                                         rate=self._wav_file.getframerate(),
                                         output=True)
        self.effect_loop()

    def effect_loop(self):

        # @TODO remove if not necessary - not used yet
        while not self._stop_event.is_set():

            data = self._wav_file.readframes(self._chunk)
            while data != b'':
                self._stream.write(data)
                data = self._wav_file.readframes(self._chunk)

            print("Rewind")
            self._wav_file.rewind()
            try:
                bpm = self._queue.get_nowait()
                self._currentBpm = bpm if bpm > 0 else self._currentBpm
                print("Received bpm from dispatcher: " + str(self._currentBpm))
            except queue.Empty:
                pass

            print("sleep..")
            time.sleep(60/self._currentBpm)     # adjust pause between heartbeats
            print("wakeup!")

        print("Stopping " + self.name)
