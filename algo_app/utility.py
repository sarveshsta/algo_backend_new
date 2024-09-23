import requests

def run_strategy(dict, user_id):
    url = "http://localhost:5000/strategy/start_strategy"
    body = {
        "user_id": user_id,
        "strategy_id": dict.get("strategy_id"),
        "index": dict.get("index"),
        "strike_price": dict.get("strike_price"),
        "expiry": dict.get("expiry"),
        "option": dict.get("option"),
        "chart_time": dict.get("chart_time")
    }
    response = requests.post(url=url, data=body)
    return response.json()


def stop_strategy(strategy_id):
    url = "http://localhost:5000/strategy/stop_strategy/{strategy_id}"
    response = requests.get(url=url)
    return response.json()


def previous_orders(user_id):
    url = "http://localhost:5000/tokens/order/{user_id}"
    response = requests.get(url=url)
    return response.json()