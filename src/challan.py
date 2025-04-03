from twilio.rest import Client

# Twilio credentials
account_sid = "your_account_sid"
auth_token = "your_auth_token"
twilio_phone = "+1234567890"
owner_phone = "+919876543210"

client = Client(account_sid, auth_token)

def send_challan(speed):
    message = f"Your vehicle was detected overspeeding at {speed:.2f} km/h. Please pay the fine."
    client.messages.create(
        body=message,
        from_=twilio_phone,
        to=owner_phone
    )
    print("E-Challan sent successfully!")
