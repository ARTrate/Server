import sys
from pythonosc import dispatcher, osc_server
import argparse
from mido import Message


def bridge_to_midi(addr, value):
    msg = Message('note_on', value)
    print("got data...")
    print(msg)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="localhost",
                        help="The ip to listen on")
    parser.add_argument("--port", type=int, default=7099,
                        help="The port to listen on")
    args = parser.parse_args()

    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/midi", bridge_to_midi)

    server = osc_server.ThreadingOSCUDPServer((args.ip, args.port), dispatcher)
    print("Serving on {}".format(server.server_address))
    try:
        server.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
