from time import sleep

from PyDMXControl import Colors
from PyDMXControl.controllers import uDMXController as Controller
from PyDMXControl.effects.Color import Chase
from PyDMXControl.effects.Intensity import Dim
from PyDMXControl.profiles.Stairville import LED_Par_10mm, LED_Par_36
from PyDMXControl.profiles.defaults import Fixture
from PyDMXControl.profiles.defaults import Vdim


class LED_Zoom_Wash_Moving(Vdim):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._register_channel('dimmer')
        self._register_channel('red', vdim=True)
        self._register_channel_aliases('red', 'r')
        self._register_channel('green', vdim=True)
        self._register_channel_aliases('green', 'g')
        self._register_channel('blue', vdim=True)
        self._register_channel_aliases('blue', 'b')
        self._register_channel('white', vdim=True)
        self._register_channel_aliases('white', 'w')
        self._register_channel('full_dimmer')
        self._register_channel('pan')
        self._register_channel('tilt')
        self._register_channel('pan_fine')
        self._register_channel('tilt_fine')
        self._register_channel('speed')
        self._register_channel('focus')
        self._register_channel('strobe')

dmx = Controller()


# Fixtures
dmx.add_fixture(LED_Zoom_Wash_Moving)

# Dim all up
dmx.all_locate()

# Test color chase
Chase.group_apply(dmx.get_all_fixtures(), 1000, colors=[Colors.Red, Colors.Yellow, Colors.Green, Colors.Blue])

# Wait then clear
sleep(10)
dmx.clear_all_effects()
dmx.all_locate()
sleep(5)

# Test color chase
Chase.group_apply(dmx.get_all_fixtures(), 5000, colors=[Colors.Blue, Colors.Cyan, Colors.White])

# Wait then clear
sleep(15)
dmx.clear_all_effects()
dmx.all_locate()
sleep(5)

# Test dim chase
dmx.all_off()
Dim.group_apply(dmx.get_fixtures_by_profile(LED_Par_36), 1000)

# Debug
dmx.debug_control()

# Done
dmx.sleep_till_enter()
dmx.close()
