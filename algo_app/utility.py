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
    url = f"{settings.FASTAPI_BASE_URL}{fastapi_routes.STOP_STRATEGY}?strategy_id={strategy_id}"
    response = requests.post(url=url)
    return response.json()

def strategy_status(strategy_id):
    url = f"{settings.FASTAPI_BASE_URL}{fastapi_routes.STRATEGY_STATUS}?strategy_id={strategy_id}"
    response = requests.post(url=url)
    return response.json()

def connect_account(dict, user_id):
    url = f"{settings.FASTAPI_BASE_URL}{fastapi_routes.CONNECT_ACCOUNT}"
    body = {
        "client_code": dict.get("client_code"),
        "password": dict.get("password"),
        "totp_secret": dict.get("totp_secret"),
        "api_key" : dict.get("api_key")
    }

    response = requests.post(url=url, json=body)
    res_data = response.json()

    if res_data.get("success") == True:
        user = User.objects.get(id=user_id)

        AngelOneCredential.objects.create(
            user=user,
            client_code=dict.get("client_code"),
            password=dict.get("password"),       
            totp_secret=dict.get("totp_secret"), 
            api_key=dict.get("api_key"), 
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




def trade_details(user_id, email):
    try:
        url = f"{settings.FASTAPI_BASE_URL}/tokens/trades_details/"
        token = generate_encrypted_token(user_id,email)
        headers = {"Authorization": token}
        response = requests.get(url=url, headers=headers)
        return response.json()
    except Exception as e:
        raise Exception(f"error-- {str(e)}")

def trade_detail(user_id, email):
    try:
        url = f"{settings.FASTAPI_BASE_URL}/tokens/trades/"
        token = generate_encrypted_token(user_id,email)
        headers = {"Authorization": token}
        response = requests.get(url=url, headers=headers)
        return response.json()
    except Exception as e:
        raise Exception(f"error-- {str(e)}")
