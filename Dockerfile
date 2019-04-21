FROM ubuntu:latest
RUN apt-get update

RUN apt-get install -y -q build-essential python-pip python-dev python-simplejson git
RUN pip install --upgrade pip
RUN pip install --upgrade virtualenv


RUN mkdir deployment
RUN git clone https://github.com/jlsomeg/TFG---RestFul-Web-App-Using-Python-Flask-and-MySQL-.git /deployment/
RUN pip install -r requirements.txt
RUN virtualenv /deployment/env/
RUN /deployment/env/bin/pip install flask
WORKDIR /deployment
CMD env/bin/set FLASK_APP=mysql-test.py
CMD env/bin/python -m flask run
