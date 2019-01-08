import os
import time
import argparse
from pythonosc import udp_client
from acc_sensor_rr.Code.ImportCsv import ImportCsv as csv


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="app",
                        help="The ip of the OSC server")
    parser.add_argument("--port", type=int, default=5005,
                        help="The port the OSC server is listening on")
    parser.add_argument("--file", help="CSV with ACC Data")
    args = parser.parse_args()

    client = udp_client.SimpleUDPClient(args.ip, args.port)
    print("Client up...")
    print("reading csv...")
    directory = os.path.dirname(__file__)
    filename = os.path.join(directory, args.file)
    import_csv = csv(filename)
    acc_data = import_csv.import_csv()
    print(acc_data[0])

    for entry in range(len(acc_data)):
        value_array = [x.strip() for x in str(acc_data[entry]).split(',')]
        value_array = [x.strip(')') for x in value_array]
        value_array = value_array[1:]
        value_string = str(value_array)
        value_string = value_string.replace("[", "")
        value_string = value_string.replace("]", "")
        value_string = value_string.replace(" ", "")
        value_string = value_string.replace("'", "")
        client.send_message("/RR", value_string)
        print("client sent " + value_string + " raw acc data")
        # time.sleep(0.02)
