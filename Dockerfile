FROM arm64v8/python:3.8-slim-buster 
RUN apt-get update \
    && apt-get install libgl1-mesa-dev libglib2.0-dev vim net-tools wget ntp -y
RUN mkdir -p /bankapp/deploy/face_pic
WORKDIR /bankapp/deploy/
COPY ./requirements.txt /bankapp/deploy/
RUN pip install -q -r ./requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple 
COPY ./capture.py /bankapp/deploy/
COPY ./test_face.py /bankapp/deploy/
COPY ./startup.sh /bankapp/deploy/
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime 
RUN chmod -R 777 /bankapp/deploy
CMD sh ./startup.sh
