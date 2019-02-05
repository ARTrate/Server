from enum import Enum


class SoundMode(Enum):
    AVERAGE = 1
    DIFFERENCE = 2


HEARTBEAT_TIMEOUT = 5               # Nr of unsuccessfull polls on bpm queue before going into idle mode
SOUNDFILE_DIR = "media/"            # Path to wav file directory
SOUND_MODE = SoundMode.DIFFERENCE   # Mode of SoundEffectEngine
AVG_WINDOW = 2                      # Nr of bpm values to be stored (for Difference mode, keep at least a window of 2!)
BPM_RANGE_LOW = 50                  # BPM range (inclusive) to assign wav files to (everything lower/higher than given
BPM_RANGE_HIGH = 99                 # range will be capped. Total range should be dividable by number of wav files.
HISTORY_DIR = "../hist/"            # Directory where the hist files are put - if started with "/" it will take absolute
                                    # path, otherwise relative path
PLOT_BPM = True
PLOT_RR = False
PLOT_INTERVAL = 3000                # Plot update interval in ms
PLOT_WINDOW = 4
