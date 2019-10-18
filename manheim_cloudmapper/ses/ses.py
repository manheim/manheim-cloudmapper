import os
import boto3
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

class SES():

    # The character encoding for the email.
    CHARSET = "utf-8"

    # Specify a configuration set. If you do not want to use a configuration
    # set, comment the following variable, and the 
    # ConfigurationSetName=CONFIGURATION_SET argument below.
    #CONFIGURATION_SET = "ConfigSet"

    def __init__(self, region):
        """
        Initialize the SES provider

        :param region: AWS region for SES
        :type region: str
        """
        self.region = region

        # Create a new SES resource
        self.client = boto3.client('ses',region_name=region)

    def send_email(self, sender, recipient, subject, body_text, body_html, attachments):
        """
        Send a raw email using AWS SES

        :param sender: From address
        :type sender: str
        :param recipient: To Address
        :type recipiend: str
        :param subject: Email subject
        :type subject: str
        :param body_text: Email Body Text (displayed in clients that do not support html emails)
        :type body_text: str
        :param body_html: HTML comtents of the email
        :type body_html: str
        :param attachments: Attachments for the email
        :type attachments: list
        """

        # Create a multipart/mixed parent container.
        msg = MIMEMultipart('mixed')
        # Add subject, from and to lines.
        msg['Subject'] = subject 
        msg['From'] = sender
        msg['To'] = recipient

        # Create a multipart/alternative child container.
        msg_body = MIMEMultipart('alternative')
        # Encode the text and HTML content and set the character encoding. This step is
        # necessary if you're sending a message with characters outside the ASCII range.
        textpart = MIMEText(body_text.encode(self.CHARSET), 'plain', self.CHARSET)
        htmlpart = MIMEText(body_html.encode(self.CHARSET), 'html', self.CHARSET)

        # Add the text and HTML parts to the child container.
        msg_body.attach(textpart)
        msg_body.attach(htmlpart)

        for attachment in attachments:
            # Define the attachment part and encode it using MIMEApplication.
            att = MIMEApplication(open(attachment, 'rb').read())

            # Add a header to tell the email client to treat this part as an attachment,
            # and to give the attachment a name.
            att.add_header('Content-Disposition','attachment',filename=os.path.basename(attachment))

            # Attach the multipart/alternative child container to the multipart/mixed
            # parent container.
            msg.attach(msg_body)

            # Add the attachment to the parent container.
            msg.attach(att)

        #print(msg)
        try:
            #Provide the contents of the email.
            response = self.client.send_raw_email(
                Source=sender,
                Destinations=[
                    recipient
                ],
                RawMessage={
                    'Data':msg.as_string(),
                }
            )
        # Display an error if something goes wrong.	
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            print("Email sent! Message ID:"),
            print(response['MessageId'])


