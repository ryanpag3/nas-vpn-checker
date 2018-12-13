import json, socket, requests, boto3, datetime # pylint: disable=import-error
from dotmap import DotMap
from twilio.rest import Client # pylint: disable=import-error
from botocore.exceptions import ClientError # pylint: disable=import-error

config_file = open('config.json', 'r')
config = json.load(config_file)
config = DotMap(config)
print(config.twilio)
twilio_client = Client(config.twilio.account_id, config.twilio.account_secret)
ses_client = boto3.client('ses', config.aws.ses.region)

def main():
    run_check()

def run_check():
    ip = config['ip']
    curr_ip = get_curr_ip()
    if ip == curr_ip:
        alert()

def alert():
    if config.phone.sender != "":
        alert_phone()
    if config.aws.ses.sender != "":
        alert_email()

def alert_phone():
    message = twilio_client.messages.create(
        body="Your VPN on your NAS is down. You should check on it!",
        from_=config.phone.sender,
        to=config.phone.recipient
    )

def alert_email():
    try:
        response = ses_client.send_email(
            Destination={
                'ToAddresses': [
                    config.aws.ses.recipient
                ]
            },
            Message={
                'Body': {
                    'Text': {
                        'Charset': 'UTF-8',
                        'Data': str(datetime.datetime.now())
                    }
                },
                'Subject': {
                    'Charset': 'UTF-8',
                    'Data': 'ALERT: NAS VPN Down'
                }
            },
            Source=str(config.aws.ses.sender)
        )
    # Display an error if something goes wrong.	
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])

def get_curr_ip():
    return requests.get('https://api.ipify.org').text

if __name__ == "__main__":
    main()