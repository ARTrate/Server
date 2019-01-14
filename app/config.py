from enum import Enum


class SoundMode(Enum):
    AVERAGE = 1
    DIFFERENCE = 2


HEARTBEAT_TIMEOUT = 5
SOUNDFILE_DIR = "media/"
SOUND_MODE = SoundMode.AVERAGE
AVG_WINDOW = 1
# Total range should be dividable by number of wav files --> otherwise not all samples are used
BPM_RANGE_LOW = 50
BPM_RANGE_HIGH = 99
