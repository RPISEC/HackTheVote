FROM htv2024:pwn_base as base

FROM base as build

# Space-separated list of required packages
ARG REQUIRED_PACKAGES="build-essential cmake wget unzip pkg-config libncursesw5-dev libcurl4-gnutls-dev zlib1g-dev libgcrypt20-dev libgnutls28-dev"

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ${REQUIRED_PACKAGES} \
    && rm -rf /var/lib/apt/lists/*

COPY build.sh /build.sh
COPY src/ /src/
RUN mkdir /handout
RUN cd / && chmod +x /build.sh && /build.sh
RUN tar -czf /handout.tar.gz /handout

FROM base as run

# Space-separated list of required packages
ARG REQUIRED_PACKAGES="libcurl4-gnutls-dev socat"

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ${REQUIRED_PACKAGES} \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build /handout.tar.gz /handout.tar.gz
COPY --from=build /src/challenge /home/challenge_user/challenge
COPY --from=build /src/chal.patch /home/challenge_user/chal.patch
RUN cd / && tar -xz --strip-components=1 -vf /handout.tar.gz

COPY make_handout.sh /make_handout.sh
RUN cd / && chmod +x /make_handout.sh && /make_handout.sh

WORKDIR /home/challenge_user

COPY ./flag.txt flag.txt

USER challenge_user

ENTRYPOINT [ "socat", "TCP-LISTEN:31337,reuseaddr,fork", "EXEC:./challenge,raw,pty,echo=0" ]
