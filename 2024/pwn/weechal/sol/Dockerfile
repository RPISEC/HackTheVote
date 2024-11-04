FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        python3 \
        python3-pip \
        ruby \
        binutils-multiarch \
        gdb \
        gdbserver \
        git \
        vim \
        tmux \
        net-tools \
        netcat \
        wget \
        unzip

RUN python3 -m pip install pwntools
RUN gem install one_gadget
RUN git clone https://github.com/longld/peda.git ~/peda
RUN echo "source ~/peda/peda.py" >> ~/.gdbinit

RUN mkdir solve

COPY handout /solve
COPY solve.py /solve
RUN mv /solve/weechat /

WORKDIR /solve

COPY entry.sh /solve
RUN chmod +x entry.sh

ENTRYPOINT [ "tmux", "new-session", "./entry.sh" ]
