import requests
import json

request = requests.get(
    "https://auth.robokassa.ru/Merchant/Indexjson.aspx?",
)

print(json.dumps(indent=3, obj=request.json()))
