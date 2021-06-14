FROM python:3.8
MAINTAINER Mark C

# Add Tini
RUN apk add --update tini

COPY . /app
WORKDIR /app

RUN pip install -r requirement.txt
RUN git clone https://github.com/britkat1980/giv_tcp.git

EXPOSE 6345

ENTRYPOINT ["/sbin/tini", "--"]
CMD ["gunicorn", "-w 3", "-b :6345", "read:giv_api"]
