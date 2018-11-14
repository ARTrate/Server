FROM python:3

RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install python-osc argparse pyaudio

WORKDIR /usr/local/app
ADD . ./

CMD ["python", "-u", "./osc_server.py"]
#CMD ["python", "-u", "./test.py"]