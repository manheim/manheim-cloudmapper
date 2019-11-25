Changelog
=========

0.1.7 (2019-11-25)
------------------

* Skip cloudmapper collect step when SES is not enabled.
* Only run public port check unless otherwise specified.
* Enable DEBUG output for cloudmapper public runs

0.1.6 (2019-11-21)
------------------

* Skip cloudmapper report step when SES is not enabled


0.1.5 (2019-11-18)
------------------

* Add back in patch command to fix issue https://github.com/duo-labs/cloudmapper/issues/540
* The issue is that publicly accessible RDS instances have .DBSubnetGroup.Subnets set to null.

0.1.4 (2019-11-15)
------------------

* Build docker image from 2.7.4 manheim/cloudmapper fork.

0.1.3 (2019-11-15)
------------------

* Build docker image from manheim/cloudmapper fork. This adds support for boto retries.
* Revert patch command from version 0.1.2

0.1.2 (2019-11-08)
------------------

* Add patch command to fix this issue https://github.com/duo-labs/cloudmapper/issues/540
* The issue is that .DBSubnetGroup.Subnets[] is expected to exist in a data structure, but in some cases it doesn't.

0.1.1 (2019-11-06)
------------------

* Add account name to datadog event for fixing query results

0.1.0 (2019-10-31)
------------------

* Initial Version
