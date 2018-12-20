import argparse
from pythonosc import dispatcher, osc_server
from queue import Queue
import sound_effect_engine

effectEngines = []
effectEngineQueues = {}
started_effect_engines = False
started_RR_postprocessing = False


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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="app", help="The ip to listen on")
    parser.add_argument("--port", type=int, default=5005,
                        help="The port to listen on")
    args = parser.parse_args()

    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/bpm", dispatch_effect_engines)

    # @TODO: go back to single list of engine objects if this doesn't fix bug
    effectEngineQueues["SoundEffectEngine"] = Queue()
    effectEngines.append(sound_effect_engine.SoundEffectEngine(
                        effectEngineQueues.get("SoundEffectEngine")))

    server = osc_server.ThreadingOSCUDPServer((args.ip, args.port), dispatcher)
    print("Serving on {}".format(server.server_address))
    server.serve_forever()
