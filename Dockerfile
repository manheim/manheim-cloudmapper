FROM python:3.7-slim as cloudmapper

ARG git_version
ARG cloudmapper_version

WORKDIR /opt/manheim_cloudmapper

RUN apt-get update -y
RUN apt-get -y install build-essential git autoconf automake libtool python3.7-dev python3-tk jq awscli python3-pip curl
RUN apt-get install -y bash

RUN git clone --branch boto_max_attempts https://github.com/manheim/cloudmapper.git /opt/manheim_cloudmapper

RUN mkdir /opt/manheim_cloudmapper/port_check
COPY manheim_cloudmapper/* /opt/manheim_cloudmapper/

COPY manheim_cloudmapper/port_check/ /opt/manheim_cloudmapper/port_check/
COPY manheim_cloudmapper/ses/ /opt/manheim_cloudmapper/ses/

# Patch to fix this issue https://github.com/duo-labs/cloudmapper/issues/540
RUN patch /opt/manheim_cloudmapper/shared/nodes.py < nodes.patch

RUN chmod +x /opt/manheim_cloudmapper/cloudmapper.sh

RUN pip install pipenv
RUN pipenv install premailer --skip-lock
RUN pipenv install --skip-lock

ENTRYPOINT /opt/manheim_cloudmapper/cloudmapper.sh

LABEL com.manheim.commit=$git_version \
      org.opencontainers.image.revision=$cloudmapper_version \
      com.manheim.repo="https://github.com/manheim/manheim-cloudmapper.git" \
      org.opencontainers.image.source="https://github.com/manheim/manheim-cloudmapper.git" \
      org.opencontainers.image.url="https://github.com/manheim/manheim-cloudmapper" \
      org.opencontainers.image.authors="man-releaseengineering@manheim.com"
      