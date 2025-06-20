import razorpay
from django.conf import settings

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def create_razorpay_plan(plan):
    print(client.order.all()) 
    data = {
    "period": "monthly",  # must be daily, weekly, monthly, or yearly
    "interval": 1,        #must be ≥1
    "item": {
        "name": "Your Plan Name",
        "description": "Some description",
        "amount": 50000,    #in paise
        "currency": "INR"
    }
    }
    return client.plan.create(data)


def create_razorpay_subscription(plan_id, customer_email):
    data = {
        "plan_id": plan_id,
        "customer_notify": 1,
        "total_count": 1,
        "notify_info": {
            "email": customer_email
        }
    }
    return client.subscription.create(data)


def create_razorpay_order(amount):
    data = {
        "amount": int(amount * 100),  # in paise
        "currency": "INR",
        "payment_capture": 1
    }
    return client.order.create(data)


def verify_signature(data):
    try:
        client.utility.verify_payment_signature(data)
        return True
    except razorpay.errors.SignatureVerificationError:
        return False
