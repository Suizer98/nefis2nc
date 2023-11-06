# If we managed to find libnefis.so share library file
FROM ubuntu:20.04

# ensure local python is preferred over distribution python
ENV PATH /usr/local/bin:$PATH

WORKDIR /app
ADD . /app

# Set environment variables for non-interactive apt
ENV DEBIAN_FRONTEND=noninteractive

# Install required packages
RUN set -xe \
    && apt-get update -y --no-install-recommends \
    && apt-get install -y --no-install-recommends \
        python2.7 \
        python-dev \
        python-tk \
        curl \
        ca-certificates \
        build-essential \
        libhdf5-dev \
        libnetcdf-dev

# Install pip for Python 2.7
RUN curl -O https://bootstrap.pypa.io/pip/2.7/get-pip.py
RUN python2.7 get-pip.py

COPY . .

WORKDIR /app/stompy
RUN pip2 install --upgrade setuptools
RUN pip2 install -e .
RUN pip2 install configparser
RUN pip2 install pandas
RUN pip2 install numpy
RUN pip2 install matplotlib
RUN pip2 install netCDF4==1.1.7.1
RUN pip2 install scipy

WORKDIR /app
# CMD ["python2.7", "trih2nc.py"]
