FROM ubuntu:20.04
RUN apt-get update && apt-get install libpq-dev python-dev python3-pip -y
RUN mkdir myroot
WORKDIR /myroot
ADD . /myroot
RUN pip3 install -r /myroot/requirements.txt
RUN chmod +x runserver.sh