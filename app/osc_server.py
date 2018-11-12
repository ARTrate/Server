import argparse
from pythonosc import dispatcher, osc_server


def dispatchEffectEngines(addr, args):
  print("+++++++ RECEIVED OSC DATA +++++++ ")

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--ip",
      default="app", help="The ip to listen on")
  parser.add_argument("--port",
      type=int, default=5005, help="The port to listen on")
  args = parser.parse_args()
  
dispatcher = dispatcher.Dispatcher()
dispatcher.map("/bpm", dispatchEffectEngines)

server = osc_server.ThreadingOSCUDPServer(
      (args.ip, args.port), dispatcher)
print("Serving on {}".format(server.server_address))
server.serve_forever()
