import argparse
from pythonosc import dispatcher, osc_server
from queue import Queue
from sound_effect_engine import *

effectEngines = [SoundEffectEngine(Queue())]
started = False

def dispatchEffectEngines(addr, args):
    global started
    global effectEngines
    print("+++++++ DISPATCH OSC DATA +++++++ ")
    for e in effectEngines:
        if not started:
            e.start()
        e.get_queue().put(args)
    started = True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="app", help="The ip to listen on")
    parser.add_argument("--port", type=int, default=5005, help="The port to listen on")
    args = parser.parse_args()
  
    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/bpm", dispatchEffectEngines)

    server = osc_server.ThreadingOSCUDPServer((args.ip, args.port), dispatcher)
    print("Serving on {}".format(server.server_address))
    server.serve_forever()

