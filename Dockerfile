FROM python:3.7-slim-buster 
RUN apt-get update \
    && apt-get install libgl1-mesa-dev vim net-tools wget -y
RUN mkdir -p /bankapp/deploy/
COPY ./* /bankapp/deploy/
WORKDIR /bankapp/deploy/
RUN pip install -q -r ./requirements.txt
CMD python capture.py
