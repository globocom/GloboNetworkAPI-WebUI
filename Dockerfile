FROM python:2.7

RUN mkdir -p /netapi_webui
WORKDIR /netapi_webui

ADD . /netapi_webui/

CMD cd /netapi_webui

EXPOSE 8080

RUN apt-get update
RUN apt-get install libldap2-dev libsasl2-dev libssl-dev -y
RUN apt-get install python-ldap -y
RUN apt-get install net-tools dnsutils -y

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
#RUN pip install -r requirements_test.txt
RUN pip install virtualenv
RUN pip install gunicorn
