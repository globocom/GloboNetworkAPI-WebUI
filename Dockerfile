FROM python:2.7

RUN mkdir -p /netapi_webui
WORKDIR /netapi_webui

ADD . /netapi_webui/

CMD cd /netapi_webui

EXPOSE 8080

RUN apt-get update && \
    apt-get install -y libldap2-dev \
                       libsasl2-dev \
                       libssl-dev \
                       python-ldap \
                       net-tools \
                       dnsutils

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install virtualenv
RUN pip install gunicorn
