FROM ubuntu:15.04

RUN apt-get update && \
    apt-get install -y \
    python-numpy python3 python3-pip libfreetype6-dev g++ python3.4-dev pkg-config git 

RUN mkdir /home/nobody && \
    chown nobody /home/nobody
USER nobody
ENV HOME=/home/nobody \
    PATH=/home/nobody/.local/bin:$PATH \
    LANG=en_GB.UTF-8
# LANG needed for httpretty install on Py3
WORKDIR /home/nobody

COPY requirements.txt /home/nobody/requirements.txt
RUN pip3 install --user -r requirements.txt

COPY . /home/nobody/
USER root
RUN chown -R nobody /home/nobody
USER nobody

ENTRYPOINT ["python3", "main_route.py"]
EXPOSE 5000
