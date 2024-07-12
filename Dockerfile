FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    libusb-1.0-0-dev \
    freeglut3-dev \
    libxmu-dev \
    libxi-dev \
    libglib2.0-0 \
    python3 \
    python3-dev \
    python3-pip \
    python3-numpy \
    cython \
    x11-utils \
    x11-xserver-utils

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

RUN git clone https://github.com/OpenKinect/libfreenect.git /usr/local/src/libfreenect && \
    cd /usr/local/src/libfreenect && \
    mkdir build && \
    cd build && \
    cmake .. -DBUILD_PYTHON3=ON && \
    make && \
    make install && \
    ldconfig /usr/local/lib && \
    cd /usr/local/src/libfreenect/wrappers/python && \
    python3 setup.py install

WORKDIR /app

COPY src /app/src
COPY images /app/images

CMD ["python3", "src/main.py"]