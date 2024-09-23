from twilio.rest import Client
from algo_today.settings import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN

def send_otp(otp, to_number):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    client.messages.create(
            body = f'Greetings, your OTP for Algo-Today is {otp}. Please do not share it with anyone.',
            from_= '+12136529736',
            to = '+91' + str(to_number)
        )

