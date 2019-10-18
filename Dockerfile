FROM python:3.7-slim as cloudmapper

ARG git_version

WORKDIR /opt/cloudmapper

RUN apt-get update -y
RUN apt-get -y install build-essential git autoconf automake libtool python3.7-dev python3-tk jq awscli python3-pip
RUN apt-get install -y bash

RUN git clone https://github.com/duo-labs/cloudmapper.git /opt/cloudmapper

RUN mkdir /opt/cloudmapper/port_check
COPY manheim_cloudmapper/* /opt/cloudmapper/

COPY manheim_cloudmapper/port_check/ /opt/cloudmapper/port_check/
COPY manheim_cloudmapper/ses/ /opt/cloudmapper/ses/

RUN chmod +x /opt/cloudmapper/cloudmapper.sh

RUN pip install pipenv
RUN pipenv install premailer --skip-lock
RUN pipenv install --skip-lock

RUN bash

LABEL com.manheim.commit=$git_version \
      org.opencontainers.image.revision=$git_version \
      com.manheim.repo="https://github.com/manheim/manheim-cloudmapper.git" \
      org.opencontainers.image.source="https://github.com/manheim/manheim-cloudmapper.git" \
      org.opencontainers.image.url="https://github.com/manheim/manheim-cloudmapper" \
      org.opencontainers.image.authors="man-releaseengineering@manheim.com"
      