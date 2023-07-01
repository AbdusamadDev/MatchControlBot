# import requests
# import json
#
# json_data = """
#     {
#       "chat_id": 5122119678,
#       "title": "1 Матч (нерег)",
#       "description": "орорп",
#       "payload": "test",
#       "provider_token": "5740929568:TEST:638231691315956867",
#       "currency": "RUB",
#       "prices": [
#         {
#           "label": "Руб",
#           "amount": 2500
#         }
#       ]
#     }
# """
#
# data = json.loads(json_data)  # Convert the JSON string to a dictionary
#
# request = requests.post("https://auth.robokassa.kz/Merchant/Index.aspx", json=data)
#
# # print(request.json())
# """        <?
#           $mrh_login = "Test1999";
#           $mrh_pass1 = "password_1";
#           $inv_id = 678678;
#           $inv_desc = "Товары для животных";
#           $out_summ = "100.00";
#           $IsTest = 1;
#           $crc = md5("$mrh_login:$out_summ:$inv_id:$mrh_pass1");
#           print "<html><script language=JavaScript ".
#             "src='https://auth.robokassa.ru/Merchant/PaymentForm/FormMS.js?".
#             "MerchantLogin=$mrh_login&OutSum=$out_summ&InvoiceID=$inv_id".
#
#         "&Description=$inv_desc&SignatureValue=$crc&IsTest=$IsTest'></script></html>";
#         ?>"""
# d = [
#     {'capitan_id': '5122119678', 'user_fullname': 'sdfjklhsjklghsdfgcvbwer'},
#     {'capitan_id': '5122119678', 'user_fullname': 'vbd'},
#     {'capitan_id': '5122119678', 'user_fullname': 'ewrgh'},
#     {'capitan_id': '5122119678', 'user_fullname': 'sdfbvxc'},
#     {'capitan_id': '5122119678', 'user_fullname': 'rhsywrst'},
#     {'capitan_id': '5122119678', 'user_fullname': 'hbvjd'},
#     {'capitan_id': '5122119678', 'user_fullname': 'sfgb'}
# ]
# del d[0]
# for i in d:
#     print(i)

d = [
    # {'capitan_id': '5122119678', 'user_fullname': 'sdfjklhsjklghsdfgcvbwer'},
    # {'capitan_id': '5122119678', 'user_fullname': 'vbd'}
]

print(bool(d))
