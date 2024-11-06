FROM ubuntu:22.04

LABEL maintainer="cschu1981@gmail.com"
LABEL version="2.16.2"
LABEL description="mgexpose - detecting mobile genetic elements"


ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt-get install -y wget python3-pip git gawk


# ADD /home/runner/work/MGExpose/MGExpose /opt/mgexpose
RUN mkdir -p /opt/software && \
	cd /opt/software && \
	git clone https://github.com/grp-bork/mgexpose && \
	cd mgexpose && \
	pip install .

# RUN cd /opt/mgexpose && pip install .
  
CMD ["mgexpose"]