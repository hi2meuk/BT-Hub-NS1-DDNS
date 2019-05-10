# ARG BUILD_FROM
# FROM $BUILD_FROM

FROM alpine:3.8

ENV LANG C.UTF-8

# Install requirements for add-on
RUN apk add --no-cache python3 && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
    rm -r /root/.cache

RUN apk add --update --no-cache py-lxml

WORKDIR /myapp

# Copy data for add-on
COPY dns_updater.py run.sh settings.json requirements.txt ./
COPY utils/*.py utils/
RUN /usr/bin/pip install -r requirements.txt

#RUN chmod a+x run.sh

ENTRYPOINT ["python3", "dns_updater.py"]
