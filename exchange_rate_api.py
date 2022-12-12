import requests

HEADERS = {"apikey": "35eedde92530dc510e2a8580"}


def exchange_rate(amount):
    url = f"https://v6.exchangerate-api.com/v6/35eedde92530dc510e2a8580/latest/USD"
    response = requests.request("GET", url, headers=HEADERS)
    data = response.json()
    ils_to_usd = data['conversion_rates']['ILS']
    price_in_usd = amount * ils_to_usd
    return price_in_usd
