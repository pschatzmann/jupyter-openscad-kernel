FROM ubuntu
MAINTAINER phil schatzmann
USER root
RUN apt-get update && apt-get install -y git curl python3 python3-pip xvfb software-properties-common x11-utils
RUN add-apt-repository ppa:openscad/releases
RUN apt update && apt install -y openscad
ENV PATH /opt/conda/envs/beakerx/bin:$PATH
RUN pip3 install jupyterlab 
WORKDIR /opt
RUN git clone https://github.com/pschatzmann/openscad-kernel
WORKDIR /opt/openscad-kernel
RUN jupyter kernelspec install iopenscad
RUN curl -sL https://deb.nodesource.com/setup_10.x | bash -
RUN apt update && apt install -y nodejs 
RUN jupyter labextension install jupyterlab-openscad-syntax-highlighting
#RUN jupyter labextension install jupyterlab-viewer-3d
CMD jupyter lab --allow-root --ip=0.0.0.0 --port=8888 --no-browser 
