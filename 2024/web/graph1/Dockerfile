ARG UBUNTU_DIGEST=sha256:aa772c98400ef833586d1d517d3e8de670f7e712bf581ce6053165081773259d
FROM --platform=linux/amd64 ubuntu@${UBUNTU_DIGEST} as base

RUN useradd challenge_user
WORKDIR /
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
	nginx \
    curl \
	python3-flask \
	gunicorn \
	python3-gunicorn \
    ca-certificates wget \
    libprotobuf23 \
    libnl-3-200 \
    libnl-route-3-200 \
	python3-pil \
	busybox-static \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /tmp/graph && chmod 777 /tmp/graph
# Versions don't actually matter
RUN curl -s http://s.minos.io/archive/bifrost/x86_64/opt-gnuplot-4.4.0-1.tar.gz | tar zx -C /tmp/graph --strip-components=3 ./opt/gnuplot/bin/gnuplot
RUN curl -sL https://github.com/johnkerl/miller/releases/download/v6.12.0/miller-6.12.0-linux-amd64.tar.gz | tar xz -C /tmp/graph/bin --strip-components=1 miller-6.12.0-linux-amd64/mlr

COPY src/ /src/

COPY /src/server /home/challenge_user/
COPY /src/sandbox.sh /usr/local/bin
RUN mkdir /handout
RUN /bin/sh /src/flaggen/setup.sh && rm -r /src/flaggen

WORKDIR /home/challenge_user

ENV SECRET_KEY="_5#y2LxF4Q8zxnxxec]/" ADMINHASH="de693c3598ca6c7203a9b0de7895029488c77706b35e37416ba0cf5b5539ba06fdfac6cf8b444ab5f449729928cd7d2370930bdaad0e4252544c285712297b1b"
ENTRYPOINT ["gunicorn", "app:app", "-w", "8", "-u", "challenge_user", "-g", "challenge_user", "--bind", "0.0.0.0:31337"]
