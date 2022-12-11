import requests

HEADERS = {"apikey": "PgMhRm9ZdKZQRmOwjUwbKBYHSOtYDbpm"}


def exchange_rate(amount):
    url = f"https://api.apilayer.com/exchangerates_data/convert?to=USD&from=ILS&amount={amount}"
    response = requests.request("GET", url, headers=HEADERS)
    data = response.json()
    er = data['result']
    print(er)


exchange_rate(3)