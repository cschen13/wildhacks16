from twilio.rest import TwilioRestClient

ACCOUNT = os.environ['ACCOUNT']
TOKEN = os.environ['TOKEN']

client = TwilioRestClient(ACCOUNT, TOKEN)

message = client.sms.messages.create(to="+12246221941",
                                     from_="+16693421879",
                                     body="Hi G Baby!")