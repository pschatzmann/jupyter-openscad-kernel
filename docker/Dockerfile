FROM alpine:edge
LABEL maintainer="phil.schatzmann@gmail.com"
RUN echo @testing http://nl.alpinelinux.org/alpine/edge/testing >> /etc/apk/repositories
RUN apk update && apk add --no-cache git  wget bash curl openscad@testing tini python python3-dev py3-pip build-base linux-headers nodejs npm xvfb xvfb-run
RUN pip3 install jupyterlab 
WORKDIR /opt
RUN git clone https://github.com/pschatzmann/openscad-kernel
WORKDIR /opt/openscad-kernel
RUN jupyter kernelspec install --user iopenscad
#RUN pip3 install jupyterlab openscad-kernel
#RUN python3 -m iopenscad.install
RUN jupyter labextension install jupyterlab-openscad-syntax-highlighting jupyterlab-viewer-3d
CMD jupyter lab --allow-root --ip=0.0.0.0 --port=8888 --no-browser 
