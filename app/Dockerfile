FROM python:3

WORKDIR /usr/local/app
ADD osc_server.py ./

RUN pip install python-osc argparse

CMD ["python", "-u", "./osc_server.py"]
