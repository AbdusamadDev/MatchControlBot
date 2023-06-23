import requests

json = """
    {
      "chat_id": 000000,
      "title": "Оплата через Робокассу",
      "description": "Описание заказа",
      "payload": "test",
      "provider_token": "1111111111:LIVE:637955761195921111",
      "currency": "RUB", 
      "prices": [
        {
          "label": "Руб",
          "amount": 10000
        }
      ]
    }
"""
request = requests.post("")
"""
after balance decrease. list of matches should be displayed
database counting not working

"""