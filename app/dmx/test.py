from pyudmx import pyudmx

dev = pyudmx.uDMXDevice()
print(dev.open())
print(dev.Device)

for i in range(1, 13):
    print(dev.send_single_value(i, 101))
dev.close()

#import array
#from ola.ClientWrapper import ClientWrapper

#def DmxSent(state):
#  wrapper.Stop()

#universe = 1
#data = array.array('B', [0, 0, 125, 125, 125])
#wrapper = ClientWrapper()
#client = wrapper.Client()
#client.SendDmx(universe, data, DmxSent)
#wrapper.Run()