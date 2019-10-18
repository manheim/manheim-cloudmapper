#!/bin/bash

# set -e
echo "Runnning Cloudmapper.sh"

echo "Copying S3 config.json file to container..."
aws s3 cp s3://$S3_BUCKET/config.json config.json
echo "S3 Copy successful!"

echo "config.json: "
cat config.json

echo "Running cloudmapper.py collect on $ACCOUNT"
pipenv run python cloudmapper.py collect --account $ACCOUNT

echo "Running cloudmapper.py report on $ACCOUNT"
pipenv run python cloudmapper.py report --account $ACCOUNT

echo "Running cloudmapper.py public scan on $ACCOUNT"
pipenv run python cloudmapper.py public --account $ACCOUNT > $ACCOUNT.json

echo "Running check on bad ports for $ACCOUNT"
pipenv run python /opt/cloudmapper/run_port_check.py

echo "Sending email via SES for $ACCOUNT"
pipenv run python /opt/cloudmapper/send_email.py

echo "Cloudmapper run was successful!"

# Send success to datadog for monitoring
curl  -X POST -H "Content-type: application/json" \
-d "{
      \"title\": \"Cloudmapper Success\",
      \"text\": \"Cloudmapper run was successful for $ACCOUNT\",
      \"priority\": \"normal\",
      \"alert_type\": \"success\"
}" \
"https://api.datadoghq.com/api/v1/events?api_key=$DATADOG_API_KEY"
