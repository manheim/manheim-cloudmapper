#!/bin/bash

set -e

echo "Runnning Cloudmapper.sh"

echo "Copying S3 config.json file to container..."
aws s3 cp s3://$S3_BUCKET/config.json config.json
echo "S3 Copy successful!"

echo "config.json: "
cat config.json

echo "Running cloudmapper.py collect on $ACCOUNT"
pipenv run python cloudmapper.py collect --account $ACCOUNT || true

if [ $SES_ENABLED == 'true' ]; then
    echo "Running cloudmapper.py report on $ACCOUNT"
    pipenv run python cloudmapper.py report --account $ACCOUNT
fi

echo "Running cloudmapper.py public scan on $ACCOUNT"
pipenv run python cloudmapper.py public --account $ACCOUNT > $ACCOUNT.json

echo "Running check on bad ports for $ACCOUNT"
mv /opt/manheim_cloudmapper/run_port_check.py /opt/run_port_check.py
pipenv run python /opt/run_port_check.py

echo "Sending email via SES for $ACCOUNT"
mv /opt/manheim_cloudmapper/send_email.py /opt/send_email.py
pipenv run python /opt/send_email.py

echo "Cloudmapper run was successful!"

# Send success to datadog for monitoring
curl  -X POST -H "Content-type: application/json" \
-d "{
        \"title\": \"Cloudmapper Success for $ACCOUNT\",
        \"text\": \"Cloudmapper run was successful for $ACCOUNT\",
        \"priority\": \"normal\",
        \"alert_type\": \"success\"
    }" \
"https://api.datadoghq.com/api/v1/events?api_key=$DATADOG_API_KEY"
