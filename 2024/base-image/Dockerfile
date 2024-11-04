ARG UBUNTU_DIGEST=sha256:aa772c98400ef833586d1d517d3e8de670f7e712bf581ce6053165081773259d

FROM --platform=linux/amd64 ubuntu@${UBUNTU_DIGEST} as base

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y ca-certificates wget

RUN useradd challenge_user

WORKDIR /

FROM --platform=linux/amd64 ubuntu@${UBUNTU_DIGEST} as build_nsjail

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    autoconf \
    bison \
    ca-certificates \
    flex \
    g++ \
    gcc \
    git \
    libnl-route-3-dev \
    libprotobuf-dev \
    libtool \
    make \
    pkg-config \
    curl \
    protobuf-compiler \
    libssl-dev && \
    rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/google/nsjail.git && make -C /nsjail

FROM base as htv2024_pwn

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    libprotobuf23 \
    libnl-3-200 \
    libnl-route-3-200 && \
    rm -rf /var/lib/apt/lists/*

COPY --from=build_nsjail /nsjail/nsjail /usr/bin/nsjail
RUN chmod 755 /usr/bin/nsjail

COPY --chown=root:root nsjail.conf /home/challenge_user/nsjail.conf
RUN chmod 400 /home/challenge_user/nsjail.conf

COPY entrypoint.sh /home/challenge_user/entrypoint.sh
RUN chmod 755 /home/challenge_user/entrypoint.sh

WORKDIR /home/challenge_user/

ENTRYPOINT ["./entrypoint.sh"]
