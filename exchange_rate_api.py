import requests

headers = {"apikey": "PgMhRm9ZdKZQRmOwjUwbKBYHSOtYDbpm"}


def exchange_rate(amount):
    url = f"https://api.apilayer.com/exchangerates_data/convert?to=USD&from=ILS&amount={amount}"
    response = requests.request("GET", url, headers=headers)
    data = response.json()
    er = data['result']
    print(er)
