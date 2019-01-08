from random import randint
import time
import argparse
from pythonosc import udp_client


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--ip", default="localhost",
      help="The ip of the OSC server")
  parser.add_argument("--port", type=int, default=5005,
      help="The port the OSC server is listening on")
  parser.add_argument("--range", action="store_true",
      help="activates range mode (generates a range of increasing bpms")
  args = parser.parse_args()

  client = udp_client.SimpleUDPClient(args.ip, args.port)
  print("Client up...")

  if args.range:
      for i in range(50, 126):
          bpm = i
          client.send_message("/bpm", bpm)
          print("client sent " + str(bpm) + " bpm")
          time.sleep(3)
  else:
      while True:
        bpm = randint(50, 120)
        client.send_message("/bpm", bpm)
        print("client sent " + str(bpm) + " bpm")
        time.sleep(4)
