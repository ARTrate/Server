# OSC Server 

the server currently connects to the test osc client by default

### Usage:
`docker build --tag osc_server .`

`docker run --device /dev/snd osc_server:latest`

`docker run --device /dev/snd osc_server:latest 'python' -u ./osc_server.py --ip <ip>`


### SoundEffects
Currently, the sound file `media/351.wav` is used (hardcoded). Will be
configurable eventually.