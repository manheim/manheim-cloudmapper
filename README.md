manheim-cloudmapper
=================

[![ReadTheDocs.org build status](https://readthedocs.org/projects/manheim-cloudmapper/badge/?version=latest)](https://manheim-cloudmapper.readthedocs.io/)

[![TravisCI build badge](https://api.travis-ci.org/manheim/manheim-cloudmapper.png?branch=master)](https://travis-ci.org/manheim/manheim-cloudmapper)

[![Docker Hub Build Status](https://img.shields.io/docker/cloud/build/manheim/manheim-cloudmapper.svg)](https://hub.docker.com/r/manheim/manheim-cloudmapper)

[![PyPI Version badge](https://img.shields.io/pypi/v/manheim-cloudmapper.svg)](https://pypi.org/project/manheim-cloudmapper/)

Manheim's Cloudmapper Docker image

This project provides common tooling, distributed as a Docker image, for managing Manheim's cloudmapper tooling. This project/repository is intended to be used (generally via the generated Docker image) alongside a configuration repository of a specific layout, containing configuration for one or more AWS accounts.

* **Full Documentation**: <https://manheim-cloudmapper.readthedocs.io/>
* TravisCI Builds: <https://travis-ci.org/manheim/manheim-cloudmapper>
* Docker image: <https://hub.docker.com/r/manheim/manheim-cloudmapper>

For documentation on the upstream cloudmapper project, please see <https://github.com/duo-labs/cloudmapper>

Introduction and Goals
----------------------

Cloudmapper is a tool designed to help analyze AWS environments. Cloudmapper contains a `public` command which is used to find public hosts and port ranges. (More details [here](https://summitroute.com/blog/2018/06/13/cloudmapper_public/).). The purpose of this repository is to run Cloudmapper remotely (on AWS) and use the `public` command to find any AWS resources which have publicly accessible ports. Alerts will then be generated and sent to PagerDuty.

Main Components
---------------

**PagerDuty Alert:** A PagerDuty alert will be generated when a public port is found that is not listed in the `OK_PORTS` environment varbiable. This varaible is set via the Terraform module specifications. (See Installation and Usage section)

**AWS SES Email:** An SES (simple email service) email is generated and sent to AWS account owners with the cloudmapper audit findings. These findings contain the public port information as well as AWS account specific information (resource counts,  audit findings, etc.). This feature is disabled by default and requires AWS SES setup to function properly. 


Installation and Usage
----------------------

This repository should only be used together with the appropriate Terraform module hosted [here](https://ghe.coxautoinc.com/MAN-TerraformModules/fargate-cloudmapper). The terraform code is where all paramters will be set for the Cloudmapper run.

See [Installation and Usage](https://manheim-cloudmapper.readthedocs.io/en/latest/usage/)