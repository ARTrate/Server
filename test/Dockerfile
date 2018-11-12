FROM python:3

RUN pip install python-osc argparse
WORKDIR /usr/local/app
ADD test_client.py ./

CMD ["python", "-u", "./test_client.py"]
