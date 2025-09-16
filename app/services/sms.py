import os
from twilio.rest import Client

def send_sms(phone, message):
    # If Twilio configured, attempt to send; otherwise log to console.
    account = os.getenv('TWILIO_ACCOUNT_SID')
    token = os.getenv('TWILIO_AUTH_TOKEN')
    from_num = os.getenv('TWILIO_FROM_NUMBER')
    if account and token and from_num and phone:
        client = Client(account, token)
        try:
            client.messages.create(body=message, from_=from_num, to=phone)
            return True
        except Exception as e:
            print('Twilio error', e)
            return False
    # fallback: print to console (useful for dev)
    print(f'[SMS-MOCK] to={phone} msg={message}')
    return True
