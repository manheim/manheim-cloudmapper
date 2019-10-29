manheim-cloudmapper
=================

[![TravisCI build badge](https://api.travis-ci.org/manheim/manheim-cloudmapper.png?branch=master)](https://travis-ci.org/manheim/manheim-cloudmapper)

[![Docker Hub Build Status](https://img.shields.io/docker/cloud/build/manheim/manheim-cloudmapper.svg)](https://hub.docker.com/r/manheim/manheim-cloudmapper)

Manheim's Cloudmapper Docker image

This project provides a Docker image for managing Manheim's cloudmapper automation. This project/repository is intended to be used (via the generated Docker image) alongside a terraform module which runs the Docker image in AWS ECS on a schedulued cycle.

* TravisCI Builds: <https://travis-ci.org/manheim/manheim-cloudmapper>
* Docker image: <https://hub.docker.com/r/manheim/manheim-cloudmapper>

For documentation on the upstream cloudmapper project, please see <https://github.com/duo-labs/cloudmapper>

Introduction and Goals
----------------------

Cloudmapper is a tool designed to help analyze AWS environments. Cloudmapper contains a `public` command which is used to find public hosts and port ranges. (More details [here](https://summitroute.com/blog/2018/06/13/cloudmapper_public/).). The purpose of this repository is to run Cloudmapper remotely (on AWS) and use the `public` command to find any AWS resources which have publicly accessible ports. Alerts will then be generated and sent to PagerDuty.

Main Components
---------------

**PagerDuty Alert:** A PagerDuty alert will be generated when a public port is found that is not listed in the `OK_PORTS` environment varbiable. (See Installation and Usage section)

**AWS SES Email:** An SES (simple email service) email is generated and sent to AWS account owners with the cloudmapper audit findings. These findings contain the public port information as well as AWS account specific information (resource counts,  audit findings, etc.). This feature is disabled by default and requires AWS SES setup to function properly. 


Installation and Usage
----------------------

**WARNING:** This project is NOT a Python package, this is a Docker image which contains cloudmapper code from [duo-labs](https://github.com/duo-labs/cloudmapper) as well as custom python code to support PagerDuty Alerting and AWS SES notifications.
