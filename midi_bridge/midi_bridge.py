import sys
from pythonosc import dispatcher, osc_server
import argparse
import mido

mido_port = 0


def bridge_to_midi(addr, value):
    global mido_port
    mido_port.send(mido.Message('control_change', channel=0, value=value, control=110))

    print("got data...")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="localhost",
                        help="The ip to listen on")
    parser.add_argument("--port", type=int, default=7099,
                        help="The port to listen on")
    args = parser.parse_args()

    mido_port = mido.open_output()

    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/midi", bridge_to_midi)

    server = osc_server.ThreadingOSCUDPServer((args.ip, args.port), dispatcher)
    print("Serving on {}".format(server.server_address))
    try:
        server.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
