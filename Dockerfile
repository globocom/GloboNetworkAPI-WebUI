FROM python:2.7

SHELL ["/bin/bash", "-c"]

RUN mkdir -p /netapi_webui
WORKDIR /netapi_webui

ADD . /netapi_webui/

CMD cd /netapi_webui

EXPOSE 8080

ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends libldap2-dev \
                       libsasl2-dev \
                       libssl-dev \
                       python-ldap \
                       net-tools \
                       dnsutils && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && \
    pip install -r requirements.txt
