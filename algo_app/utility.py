from xml.etree.ElementTree import TreeBuilder
import requests
from django.conf import settings
from algo_app.models import User,AngelOneCredential
from algo_app import fastapi_routes
from algo_app.utils import generate_encrypted_token, decrypt_encrypted_token


def start_strategy(data):
    try:
        url = f"{settings.FASTAPI_BASE_URL}{fastapi_routes.START_STRATEGY}"
        response = requests.post(url=url, json=data)
        return response.json()
    except Exception as e:
            raise Exception(f"error-- {str(e)}")


def stop_strategy(strategy_id):
    url = f"{settings.FASTAPI_BASE_URL}{fastapi_routes.STOP_STRATEGY}/{strategy_id}"
    response = requests.get(url=url)
    return response.json()



def connect_account(dict, user_id):
    if AngelOneCredential.objects.filter(user_id=user_id).exists():
        return {"status": "error", "message": "Account already connected"}

    url = f"{settings.FASTAPI_BASE_URL}{fastapi_routes.CONNECT_ACCOUNT}"
    body = {
        "client_code": dict.get("client_code"),
        "password": dict.get("password"),
        "totp_secret": dict.get("totp_secret"),
    }

    response = requests.post(url=url, json=body)
    res_data = response.json()

    if res_data.get("success") == True:
        user = User.objects.get(id=user_id)

        AngelOneCredential.objects.create(
            user=user,
            client_code=dict.get("client_code"),
            password=dict.get("password"),       
            totp_secret=dict.get("totp_secret")  
        )
    
    return res_data


def get_tokens():
    try:
        url = f"{settings.FASTAPI_BASE_URL}/tokens/"
        response = requests.get(url=url)
        return response.json()
    except Exception as e:
        raise Exception(f"error-- {str(e)}")
    

def get_index_expiry(index):
    try:
        url = f"{settings.FASTAPI_BASE_URL}/tokens/{index}"
        response = requests.get(url=url)
        return response.json()
    except Exception as e:
        raise Exception(f"error-- {str(e)}")
    

def get_index_strike_price(index, expiry):
    try:
        url = f"{settings.FASTAPI_BASE_URL}/tokens/{index}/{expiry}"
        response = requests.get(url=url)
        return response.json()
    except Exception as e:
        raise Exception(f"error-- {str(e)}")


# def previous_orders(user_id):
#     url = f"{settings.FASTAPI_BASE_URL}/tokens/order/{user_id}"
#     response = requests.get(url=url)
#     return response.json()




def trade_details():
    try:
        url = f"{settings.FASTAPI_BASE_URL}/tokens/trades_details/"
        response = requests.get(url=url)
        return response.json()
    except Exception as e:
        raise Exception(f"error-- {str(e)}")
