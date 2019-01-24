import argparse
from pythonosc import dispatcher, osc_server
from queue import Queue
import sys
import numpy
from scipy.signal import find_peaks
from sound_effect_engine import SoundEffectEngine
from acc_sensor_rr.Code.Signalprocessing import Signalprocessing
from history_controller import HistoryController
import history_data as hd
from collections import deque

LOW_CUT_RR = 0.2
HIGH_CUT_RR = 0.45

LOW_CUT_BPM = 0.7
HIGH_CUT_BPM = 3.0

SAMPLE_RATE = 50

started_effect_engines = False
started_RR_postprocessing = False
started_BPM_postprocessong = False
cached_ACC_X = deque(maxlen=3000)
cached_ACC_Y = deque(maxlen=3000)
cached_ACC_Z = deque(maxlen=3000)
cached_raw_bpm = deque(maxlen=3000)
bpm_counter = 0
rr_counter = 0

sp = Signalprocessing()

effectEngines = [SoundEffectEngine(Queue())]
historyController = HistoryController(Queue())


def dispatch_effect_engines(addr, ip, payload):
    global started_effect_engines
    global effectEngines
    print("+++++++ DISPATCH OSC DATA +++++++ ")

    for e in effectEngines:
        if not started_effect_engines:  # start threads when receiving data
            e.start()
        e.get_queue().put(payload)

    historyController.get_queue().put(hd.HistoryData(hd.HistoryDataType.BPM,
                                                     ip, payload))
    started_effect_engines = True


def postProcessRR(addr, ip, x, y, z):
    """
    Postprocess the raw acceleration data from the Sensor to extract the
    actual respiration rate. This done with the methods provided by Maximilian
    Kurscheidt

    :param addr: the OSC addr string
    :param ip: the ip of the device
    :param x: x accelleration values
    :param y: y accelleration values
    :param z: z accelleration values
    """
    global started_RR_postprocessing, rr_counter
    global cached_ACC_X, cached_ACC_Y, cached_ACC_Z
    rr_counter += 1
    x_modified = (x + 2048) * 16
    y_modified = (y + 2048) * 16
    z_modified = (z + 2048) * 16
    cached_ACC_X.append(x_modified)
    cached_ACC_Y.append(y_modified)
    cached_ACC_Z.append(z_modified)
    # print(x_modified, y_modified, z_modified)
    # if there is enough data, analyze like in Maximilian Kurscheidts` Main
    if rr_counter >= 50:
        rr_counter = 0
        raw_X = numpy.array(cached_ACC_X)
        raw_Y = numpy.array(cached_ACC_Y)
        raw_Z = numpy.array(cached_ACC_Z)

        # filter data
        filtered_X = sp.butter_bandpass_filter(raw_X, LOW_CUT_RR, HIGH_CUT_RR,
                                               SAMPLE_RATE)
        filtered_Y = sp.butter_bandpass_filter(raw_Y, LOW_CUT_RR, HIGH_CUT_RR,
                                               SAMPLE_RATE)
        filtered_Z = sp.butter_bandpass_filter(raw_Z, LOW_CUT_RR, HIGH_CUT_RR,
                                               SAMPLE_RATE)
        # FTT
        yf_X, frq_X = sp.fast_fourier_transformation(filtered_X, SAMPLE_RATE)
        yf_Y, frq_Y = sp.fast_fourier_transformation(filtered_Y, SAMPLE_RATE)
        yf_Z, frq_Z = sp.fast_fourier_transformation(filtered_Z, SAMPLE_RATE)
        # spectral power
        power_X = sp.power_of_the_spectrum(yf_X)
        power_Y = sp.power_of_the_spectrum(yf_Y)
        power_Z = sp.power_of_the_spectrum(yf_Z)

        # maximum power and frequency
        power_max, frq_max = sp.maximum_power_of_xyz_spectrum(power_X, power_Y,
                                                              power_Z,
                                                              SAMPLE_RATE)
        max_ps = sp.positive_power_spectrum_for_peak_detection(power_max)
        peak_tupel = sp.find_peak_and_frequency(max_ps, frq_max)
        rr = sp.calculate_rr_from_power_spectrum(peak_tupel)
        print("Respiration rate is: " + str(rr))


def postProcessBPM(addr, ip, raw_data: int):
    global bpm_counter, cached_raw_bpm
    bpm_counter += 1
    cached_raw_bpm.append(raw_data)
    if bpm_counter >= 50:
        bpm_counter = 0
        raw_bpm = numpy.array(cached_raw_bpm)
        filtered_bpm = sp.butter_bandpass_filter(raw_bpm, LOW_CUT_BPM,
                                                 HIGH_CUT_BPM, SAMPLE_RATE)
        peaks, _ = find_peaks(filtered_bpm)
        print("BPM: " + str(len(peaks) * (3000 / len(cached_raw_bpm))))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="localhost",
                        help="The ip to listen on")
    parser.add_argument("--port", type=int, default=5005,
                        help="The port to listen on")
    args = parser.parse_args()

    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/bpm", dispatch_effect_engines)
    dispatcher.map("/artrate/rr", postProcessRR)
    dispatcher.map("/artrate/bpm", postProcessBPM)

    # historyController.start()

    server = osc_server.ThreadingOSCUDPServer((args.ip, args.port), dispatcher)
    print("Serving on {}".format(server.server_address))
    try:
        server.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        historyController.stop()
        for engine in effectEngines:
            engine.stop()
        sys.exit()
