from random import randint
import time
import argparse
from pythonosc import osc_message_builder, udp_client
import os

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--ip", default="app",
      help="The ip of the OSC server")
  parser.add_argument("--port", type=int, default=5005,
      help="The port the OSC server is listening on")
  args = parser.parse_args()

  client = udp_client.SimpleUDPClient(args.ip, args.port)
  print("Client up...")

  while True:
    bpm = randint(50, 90)
    client.send_message("/bpm", bpm)
    print("client sent " + str(bpm) + " bpm")
    time.sleep(5)
