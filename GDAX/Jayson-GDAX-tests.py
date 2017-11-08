# Requires python-requests. Install with pip:
#
#   pip install requests
#
# or, with easy-install:
#
#   easy_install requests

import json, hmac, hashlib, time, requests, base64
from requests.auth import AuthBase

api_key = []

# Create custom authentication for Exchange
class CoinbaseExchangeAuth(AuthBase):
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = "f6afb4b847b36f9920e0d4f399e95c9e"
        self.secret_key = "meK/7bbiROSmMLL4pAi9TPVSivOk6ysLUWIB102oCPylPfdqGEZD7qq6f45iRhDHHbEVFP030IjMHAk9VL2/aQ=="
        self.passphrase = "gc4f2kyu8u5"

    def __call__(self, request):
        timestamp = str(time.time())
        message = timestamp + request.method + request.path_url + (request.body or '')
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message, hashlib.sha256)
        signature_b64 = signature.digest().encode('base64').rstrip('\n')

        request.headers.update({
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        })
        return request











#api_url = 'https://api-public.sandbox.gdax.com'
api_url = 'https://api.gdax.com/'
auth = CoinbaseExchangeAuth("d1e8bfac7390f532d4e2be575e127c39", "/Dm1q5UPdDVQUrGTAjZeVOk+oIRRTir01v5beAn64rLe3WYUVxbz+ycE7mAbUoINb9szegLspxDjXuoirTDwDw==", "wfp5fdwux")

# Get accounts
r = requests.get(api_url + 'accounts', auth=auth)

ro = requests.get(api_url + 'orders', auth=auth)

for key in r.json():
    print(key['currency'], key['balance'])
# [{"id": "a1b2c3d4", "balance":...

print('new-list-of-tuples-was-made')

tuplelistR = []
tuplelistRO = []

keylistR = r.json()
keylistRO = ro.json()



list1 = []
for i in range(10):
    list1.append( range(i,10) )

print(list1)


for key in keylistRO:
    tuple = [key['price'], key['product_id'], key['side'], key['status']]
    # print str(tuple) + "\n"
    tuplelistRO.append(tuple)

    # tuplelistrate[num].append(data[key]['rate'])

j = lambda x: x[0]

tuplelistRO.sort(key=j, reverse=False)
#return tuplelist2

print("sorted list of orders in ascending value")

for line in tuplelistRO:
    print(line)

print("And just the currencies held")

for line in tuplelistRO:
    print(line)


jsondict = json.load()


gdaxMatrixL = []

gdaxMatrix = []
#gdaxMatrix = open("./MatrixGDAX.txt", 'r')

with open('./MatrixGDAX.txt', 'r') as gdaxMatrix:
    for line in gdaxMatrix:
        gdaxMatrixL.append(eval(line)
#        gdaxMatrixL.append(line.strip().split(','))






# Place an order
order = {
    'size': 1.0,
    'price': 1.0,
    'side': 'buy',
    'product_id': 'BTC-USD',
}
r = requests.post(api_url + 'orders', json=order, auth=auth)

r





for key in keylistR:
    tuple = [key['id'], key['balance'], key['currency'], key['available']]
    # print str(tuple) + "\n"
    tuplelistR.append(tuple)

    # tuplelistrate[num].append(data[key]['rate'])

j = lambda x: x[0]

tuplelistR.sort(key=j, reverse=False)
#return tuplelist2

print("sorted list of account balances in ascending order by volume held")

for line in tuplelistR:
    print(line)

print("And just the coins held")

for line in tuplelistR:
    print(line[2])



# Place an order
order = {
    'size': 1.0,
    'price': 1.0,
    'side': 'buy',
    'product_id': 'BTC-USD',
}
r = requests.post(api_url + 'orders', json=order, auth=auth)





#gdaxholdings = []

#for line in r.json():
#    print("second")
#    print(line)
#    gdaxholdings.append(line['currency'])

#for line in gdaxholdings:
#    print("third")
#    print(line)




for key in keylist2:
    tuple = [data[key]['timestamp'], data[key]['type'], data[key]['amount'], data[key]['rate'],
             data[key]['is_your_order'], int(key)]
    # print str(tuple) + "\n"
    tuplelist2.append(tuple)

    # tuplelistrate[num].append(data[key]['rate'])

j = lambda x: x[0]

tuplelist2.sort(key=j, reverse=False)
return tuplelist2




# {"id": "0428b97b-bec1-429e-a94c-59992926778d"}
resp = btce_signed_request("TradeHistory", params)

    if resp.status_code == 200:
        data = resp.json()
        data = data.get("return")
        if data is None:
            return None

        tuplelist2 = []
        keylist2 = data.keys()

        for key in keylist2:
            tuple = [data[key]['timestamp'],  data[key]['type'], data[key]['amount'], data[key]['rate'],
                    data[key]['is_your_order'], int(key)]
            # print str(tuple) + "\n"
            tuplelist2.append(tuple)

            # tuplelistrate[num].append(data[key]['rate'])

        j = lambda x: x[0]

        tuplelist2.sort(key=j, reverse=False)
        return tuplelist2

    else:
        return None
