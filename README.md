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

To use the docker image, execute a `docker run` command  on the `manheim/manheim-cloudmapper` image. Environment varaibles are required for the docker container to execute. The recommended way to set the environment variables is with the `--env-file` flag.
```
docker run --env-file <env_file> manheim/manheim-cloudmapper:<tag>
```

env-file example:
```
S3_BUCKET=aws-account-us-east-1-cloudmapper
ACCOUNT=aws-account
DATADOG_API_KEY=abc123456
...
```

**Environment Varaibles**

| Name            | Description                                                                                                                                     | Example          |
|-----------------|-------------------------------------------------------------------------------------------------------------------------------------------------|------------------|
| S3_BUCKET       | AWS S3 bucket name where config.json file for cloudmapper is expected. This json file contains AWS account information for the cloudmapper run. | mybucket         |
| ACCOUNT         | Name of AWS account where Cloudmapper will be running                                                                                           | aws-company-prod |
| DATADOG_API_KEY | Datadog API key, for sending metrics                                                                                                            | abc123...        |
| PD_SERVICE_KEY  | PagerDuty Service Key (Events V1 integration) for alerting on critical thresholds crossed                                                       | xyz890...        |
| OK_PORTS        | A list of acceptable publicly accesible ports in string format                                                                                  | 80,443           |
| AWS_REGION      | AWS Region from which SES will send emails                                                                                                      | us-east-1        |
| SES_ENABLED     | string to enable/disable email notification via SES.                                                                                            | true             |
| SES_SENDER      | Email address of SES sender                                                                                                                     | foo@bar.com      |
| SES_RECIPIENT   | Email address of SES recipient                                                                                                                  | bar@foo.com      |

**AWS Authentication:**  
In addition to the environment variables above, the Docker container requires access to the AWS account in which cloudmapper will be run. Any method of boto3 AWS [authentication](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#credentials) is supported (environment varaibles, ~/.aws/credentials, ~/.aws/config, etc.)

When using environment varaibles, the following AWS Environment varaibles can be set in the env-file:
```
AWS_SESSION_TOKEN
AWS_DEFAULT_REGION
AWS_SECRET_ACCESS_KEY
AWS_ACCESS_KEY_ID
```

The following privilieges are required for the IAM user running cloudmapper:  
`arn:aws:iam::aws:policy/SecurityAudit`  
`arn:aws:iam::aws:policy/job-function/ViewOnlyAccess`
