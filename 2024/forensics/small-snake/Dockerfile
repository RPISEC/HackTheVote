FROM python:3.12-slim as base

FROM base as build
# Space-separated list of required packages
ARG REQUIRED_PACKAGES="build-essential"

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y --no-install-recommends ${REQUIRED_PACKAGES} && \
    rm -rf /var/lib/apt/lists/*

COPY build.sh /build.sh
COPY src/ /src/
RUN cd / && chmod +x /build.sh && /build.sh

COPY Dockerfile /handout/Dockerfile
RUN tar -czf /handout.tar.gz /handout

FROM base as run

RUN pip3 install --no-cache-dir pwntools

ARG REQUIRED_PACKAGES="qemu-system-x86-64"

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y --no-install-recommends ${REQUIRED_PACKAGES} && \
    rm -rf /var/lib/apt/lists/*

COPY --from=build /deploy /home/challenge_user/deploy

WORKDIR /home/challenge_user/deploy

COPY make_handout.sh /make_handout.sh
RUN cd / && chmod +x /make_handout.sh && /make_handout.sh

CMD ["python", "-u", "chall.py"]
