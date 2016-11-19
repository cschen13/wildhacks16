from twilio.rest import TwilioRestClient

import config

client = TwilioRestClient(config.ACCOUNT, config.TOKEN)

message = client.sms.messages.create(to="+12246221941",
                                     from_="+16693421879",
                                     body="Hi G Baby!")