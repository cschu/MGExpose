FROM ubuntu:22.04

LABEL maintainer="cschu1981@gmail.com"
LABEL version="2.16.2"
LABEL description="mgexpose - detecting mobile genetic elements"


ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt-get install -y wget python3-pip git gawk

ADD DESCRIPTION.md LICENSE README.md setup.cfg setup.py /opt/software/mgexpose/
ADD mgexpose /opt/software/mgexpose/mgexpose
ADD assets /opt/software/mgexpose/assets

WORKDIR /opt/software/mgexpose

# ADD /home/runner/work/MGExpose/MGExpose /opt/mgexpose
RUN pip install .

# RUN cd /opt/mgexpose && pip install .
  
CMD ["mgexpose"]