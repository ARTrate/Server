import argparse
from pythonosc import dispatcher, osc_server
from queue import Queue
import numpy
import sound_effect_engine
from acc_sensor_rr.Code.Signalprocessing import Signalprocessing

LOW_CUT = 0.2
HIGH_CUT = 0.45
SAMPLE_RATE = 50

effectEngines = []
effectEngineQueues = {}
started_effect_engines = False
started_RR_postprocessing = False
cached_ACC_X = []
cached_ACC_Y = []
cached_ACC_Z = []

sp = Signalprocessing()


def dispatch_effect_engines(addr, args):
    global started_effect_engines
    global effectEngines
    global effectEngineQueues
    print("+++++++ DISPATCH OSC DATA +++++++ ")
    for e in effectEngines:
        if not started_effect_engines:  # start threads when receiving data
            e.start()
        effectEngineQueues.get(e.get_name()).put(args)
    started_effect_engines = True


def postProcessRR(addr, args):
    """
    Postprocess the raw acceleration data from the Sensor to extract the
    actual respiration rate. This done with the methods provided by Maximilian
    Kurscheidt

    :param low_cut: low cut for bandpass filter
    :param high_cut: high cut for bandpass filter
    :param sample_rate: number of samples that should be analyzed
    :param addr: the OSC addr string
    :param args: the OSC payload, our value string, eg 29185,38544,28561
    """
    global started_RR_postprocessing
    global cached_ACC_X, cached_ACC_Y, cached_ACC_Z
    data_array = args.split(",")
    cached_ACC_X.append(int(data_array[0]))
    cached_ACC_Y.append(int(data_array[1]))
    cached_ACC_Z.append(int(data_array[2]))
    # if there is enough data, analyze like in Maximilian Kurscheidts` Main
    if len(cached_ACC_X) > 3000:
        raw_X = numpy.array(cached_ACC_X)
        # clean cache
        cached_ACC_X = []
        raw_Y = numpy.array(cached_ACC_Y)
        cached_ACC_Y = []
        raw_Z = numpy.array(cached_ACC_Z)
        cached_ACC_Z = []
        # filter data
        filtered_X = sp.butter_bandpass_filter(raw_X, LOW_CUT, HIGH_CUT, SAMPLE_RATE)
        filtered_Y = sp.butter_bandpass_filter(raw_Y, LOW_CUT, HIGH_CUT, SAMPLE_RATE)
        filtered_Z = sp.butter_bandpass_filter(raw_Z, LOW_CUT, HIGH_CUT, SAMPLE_RATE)
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
        print("Repsiration rate is: " + str(rr))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="app", help="The ip to listen on")
    parser.add_argument("--port", type=int, default=5005,
                        help="The port to listen on")
    args = parser.parse_args()

    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/bpm", dispatch_effect_engines)
    dispatcher.map("/RR", postProcessRR)

    # @TODO: go back to single list of engine objects if this doesn't fix bug
    effectEngineQueues["SoundEffectEngine"] = Queue()
    effectEngines.append(sound_effect_engine.SoundEffectEngine(
                        effectEngineQueues.get("SoundEffectEngine")))

    server = osc_server.ThreadingOSCUDPServer((args.ip, args.port), dispatcher)
    print("Serving on {}".format(server.server_address))
    server.serve_forever()
