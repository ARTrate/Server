import argparse
from pythonosc import dispatcher, osc_server, udp_client
from queue import Queue
import numpy
from scipy.signal import find_peaks
from sound_effect_engine import SoundEffectEngine
from acc_sensor_rr.Code.Signalprocessing import Signalprocessing
from history_controller import HistoryController
import history_data as hd
from collections import deque
import sys
import config

LOW_CUT_RR = 0.2
HIGH_CUT_RR = 0.45

LOW_CUT_BPM = 0.7
HIGH_CUT_BPM = 3.0

SAMPLE_RATE = 50
SAMPLE_RATE_RR = 12.5

started_effect_engines = False
started_RR_postprocessing = False
started_BPM_postprocessong = False
cached_ACC_X = dict()
cached_ACC_Y = dict()
cached_ACC_Z = dict()
# cached_raw_bpm = deque(maxlen=3000)
cached_raw_bpm = dict()
# bpm_counter = 0
bpm_counter = dict()
rr_counter = dict()
bpm_low_limit = 0
bpm_high_limit = 0
rr_low_limit = 0
rr_high_limit = 0

sp = Signalprocessing()

effectEngines = []
if config.ENGINE_MODE is config.EngineMode.INTERNAL:
    effectEngines.append(SoundEffectEngine(Queue()))
historyController = HistoryController(Queue())


def dispatch_internal(type, uid, payload):
    global started_effect_engines
    global effectEngines

    if type is hd.HistoryDataType.BPM:
        for e in effectEngines:
            if not started_effect_engines:  # start threads when receiving data
                e.start()
            e.get_queue().put(payload)

    if not started_effect_engines:
        historyController.start()
    historyController.get_queue().put(hd.HistoryData(type, uid, payload))
    started_effect_engines = True


def dispatch_external(type, uid, raw, ranged):
    global started_effect_engines
    osc_addr_ranged = ""
    osc_addr_raw = ""
    if type is hd.HistoryDataType.BPM:
        osc_addr_raw = "/artrate/bpm/raw/" + str(uid)
        osc_addr_ranged = "/artrate/bpm/ranged/" + str(uid)
    client.send_message(osc_addr_raw, raw)
    client.send_message(osc_addr_ranged, ranged)

    if not started_effect_engines:
        historyController.start()
    historyController.get_queue().put(hd.HistoryData(type, uid, raw))
    started_effect_engines = True


def dispatch_commercial(addr, uid, payload):

    global bpm_low_limit, bpm_high_limit
    # calculate range between 0 and 1
    ranged_value = calcRangedValue(payload, bpm_high_limit, bpm_low_limit)
    if config.ENGINE_MODE is config.EngineMode.INTERNAL:
        dispatch_internal(hd.HistoryDataType.BPM, uid, payload)

    elif config.ENGINE_MODE is config.EngineMode.EXTERNAL:
        dispatch_external(hd.HistoryDataType.BPM, uid, payload, ranged_value)


def postProcessRR(addr, uid, x, y, z):
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
    global rr_low_limit, rr_high_limit
    global started_effect_engines
    x_modified = (x + 2048) * 16
    y_modified = (y + 2048) * 16
    z_modified = (z + 2048) * 16
    if uid not in rr_counter:
        rr_counter[uid] = 0
        cached_ACC_X[uid] = deque(maxlen=3000)
        cached_ACC_Y[uid] = deque(maxlen=3000)
        cached_ACC_Z[uid] = deque(maxlen=3000)

    rr_counter[uid] += 1
    cached_ACC_X[uid].append(x_modified)
    cached_ACC_Y[uid].append(y_modified)
    cached_ACC_Z[uid].append(z_modified)

    # print(x_modified, y_modified, z_modified)
    # if there is enough data, analyze like in Maximilian Kurscheidts` Main
    if rr_counter[uid] >= 50:
        rr_counter[uid] = 0
        raw_X = numpy.array(cached_ACC_X[uid])
        raw_Y = numpy.array(cached_ACC_Y[uid])
        raw_Z = numpy.array(cached_ACC_Z[uid])

        # filter data
        filtered_X = sp.butter_bandpass_filter(raw_X, LOW_CUT_RR, HIGH_CUT_RR,
                                               SAMPLE_RATE_RR)
        filtered_Y = sp.butter_bandpass_filter(raw_Y, LOW_CUT_RR, HIGH_CUT_RR,
                                               SAMPLE_RATE_RR)
        filtered_Z = sp.butter_bandpass_filter(raw_Z, LOW_CUT_RR, HIGH_CUT_RR,
                                               SAMPLE_RATE_RR)
        # FTT
        yf_X, frq_X = sp.fast_fourier_transformation(filtered_X, SAMPLE_RATE_RR)
        yf_Y, frq_Y = sp.fast_fourier_transformation(filtered_Y, SAMPLE_RATE_RR)
        yf_Z, frq_Z = sp.fast_fourier_transformation(filtered_Z, SAMPLE_RATE_RR)
        # spectral power
        power_X = sp.power_of_the_spectrum(yf_X)
        power_Y = sp.power_of_the_spectrum(yf_Y)
        power_Z = sp.power_of_the_spectrum(yf_Z)

        # maximum power and frequency
        power_max, frq_max = sp.maximum_power_of_xyz_spectrum(power_X, power_Y,
                                                              power_Z,
                                                              SAMPLE_RATE_RR)
        max_ps = sp.positive_power_spectrum_for_peak_detection(power_max)
        peak_tupel = sp.find_peak_and_frequency(max_ps, frq_max)
        rr = sp.calculate_rr_from_power_spectrum(peak_tupel)
        # print("Respiration rate is: " + str(rr))
        # calculate range between 0 and 1
        ranged_value = calcRangedValue(rr, rr_high_limit, rr_low_limit)
        # send ranged value to ableton
        if config.ENGINE_MODE is config.EngineMode.INTERNAL:
            dispatch_internal(hd.HistoryDataType.RR, uid, rr)
        elif config.ENGINE_MODE is config.EngineMode.EXTERNAL:
            dispatch_external(hd.HistoryDataType.RR, uid, rr, ranged_value)
        print("real RR value of id " + str(uid) + ": " + str(rr))
        print("ranged RR value of id " + str(uid) + ": " + str(ranged_value))


def calcRangedValue(payload, high_lim, low_lim):
    if payload < low_lim:
        return 0.0
    elif payload > high_lim:
        return 1.0
    else:
        return (float(payload) - low_lim) / (high_lim - low_lim)


def postProcessBPM(addr, uid, raw_data: int):
    global bpm_counter, cached_raw_bpm, bpm_low_limit, bpm_high_limit
    if uid not in bpm_counter:
        bpm_counter[uid] = 0
        cached_raw_bpm[uid] = deque(maxlen=1500)

    bpm_counter[uid] += 1
    cached_raw_bpm[uid].append(raw_data)

    if bpm_counter[uid] >= 50:
        bpm_counter[uid] = 0
        raw_bpm = numpy.array(cached_raw_bpm[uid])
        filtered_bpm = sp.butter_bandpass_filter(raw_bpm, LOW_CUT_BPM,
                                                 HIGH_CUT_BPM, SAMPLE_RATE)
        peaks, _ = find_peaks(filtered_bpm)

        bpm = len(peaks) * (3000 / len(cached_raw_bpm[uid]))
        # calculate range between 0 and 1
        ranged_value = calcRangedValue(bpm, bpm_high_limit, bpm_low_limit)
        # send ranged value to ableton
        if config.ENGINE_MODE is config.EngineMode.INTERNAL:
            dispatch_internal(hd.HistoryDataType.BPM, uid, bpm)
        elif config.ENGINE_MODE is config.EngineMode.EXTERNAL:
            dispatch_external(hd.HistoryDataType.BPM, uid, bpm, ranged_value)

        print("real bpm value of id " + str(uid) + ": " + str(bpm))
        print("ranged bpm value of id " + str(uid) + ": " + str(ranged_value))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="localhost",
                        help="The ip to listen on")
    parser.add_argument("--port", type=int, default=5005,
                        help="The port to listen on")
    parser.add_argument("--ableton_ip", default="localhost",
                        help="The ip of an ableton instance")
    parser.add_argument("--ableton_port", default=7099,
                        help="The port of an ableton instance")
    parser.add_argument("--bpm_low_limit", default=40,
                        help="the low limit to calculate bpm ranges")
    parser.add_argument("--bpm_high_limit", default=120,
                        help="the high limit to calculate bpm ranges")
    parser.add_argument("--rr_low_limit", default=10,
                        help="the low limit to calculate rr ranges")
    parser.add_argument("--rr_high_limit", default=20,
                        help="the high limit to calculate rr ranges")
    args = parser.parse_args()

    bpm_low_limit = args.bpm_low_limit
    bpm_high_limit = args.bpm_high_limit
    rr_low_limit = args.rr_low_limit
    rr_high_limit = args.rr_high_limit

    if config.ENGINE_MODE is config.EngineMode.EXTERNAL:
        client = udp_client.SimpleUDPClient(args.ableton_ip, args.ableton_port)

    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/bpm", dispatch_commercial)
    dispatcher.map("/artrate/rr", postProcessRR)
    dispatcher.map("/artrate/bpm", postProcessBPM)

    server = osc_server.ThreadingOSCUDPServer((args.ip, args.port), dispatcher)
    print("Serving on {}".format(server.server_address))
    try:
        server.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        historyController.stop()
        for engine in effectEngines:
            engine.stop()
        sys.exit()
