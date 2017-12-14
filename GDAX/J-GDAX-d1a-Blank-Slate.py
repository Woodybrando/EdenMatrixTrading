# Requires python-requests. Install with pip:
#
#   pip install requests
#
# or, with easy-install:
#
#   easy_install requests

import json, hmac, hashlib, time, requests, base64
from requests.auth import AuthBase



# Create custom authentication for Exchange
class CoinbaseExchangeAuth(AuthBase):
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

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



f = open( "GDAX/config_GDAX_DONT_UPLOAD.json" , "rb" )
GDAX_config = json.load(f)
f.close()


api_url = 'https://api.gdax.com'
#api_url = 'https://api-public.sandbox.gdax.com'


GDAX_phrase = GDAX_config["GDAX_PASSPHRASE"]
GDAX_key = GDAX_config["GDAX_API_KEY"]
GDAX_secret = GDAX_config["GDAX_API_SECRET"]


auth = CoinbaseExchangeAuth( GDAX_key, GDAX_secret, GDAX_phrase)



'''
print("1")
# Get accounts
r = requests.get(api_url + 'accounts', auth=auth)
print r.json()
# [{"id": "a1b2c3d4", "balance":...
print("2")
'''

#g = requests.get(api_url + 'orders', auth=auth)

#last_fill_dealt_with = '13bed703-a95f-4397-80c3-3719e4e1d65a'
#'33bb9a38-8261-4ba1-9350-ea3827ae7335'



#f = requests.get(api_url + '/fills?product_id=LTC-USD??after={}' + str(last_fill_dealt_with), auth=auth)

#print(f.json())


order = {}
loopit = True

#run_once = 0


while loopit == True:
    run_once = 0
    last_order_file_handle = open('GDAX/last_order_id_processed.txt', 'r+')
    last_fill_dealt_with = last_order_file_handle.readline()
    print('this is the last order_id dealt with ' + last_fill_dealt_with)
    last_order_file_handle.close()

    f = requests.get(api_url + '/fills?cb-before=' + str(last_fill_dealt_with) + '&product_id=LTC-USD', auth=auth)
    print(f)


    for key in f.json():

        wait = 0

        print('    this is the most recent order_id ' + key['order_id'])

        check_key = key['order_id']

        if check_key == last_fill_dealt_with:
            print('No new trades... hold tight it will happen')
            break

        else:

            if str(key['order_id']) != last_fill_dealt_with:
                print('This order has triggered:')
                print(
                    key['price'], key['size'], key['fee'], key['side'], key['settled'], key['liquidity'], key['created_at'],
                    key['order_id'])
                # print("you triggered a " + key['side'] + " time to update your matrix!")

                if key['side'] == 'sell':
                    new_order_side = 'buy'
                    new_order_price = float(key['price'])
                    new_price = new_order_price * .992733


                elif key['side'] == 'buy':
                    new_order_side = 'sell'
                    new_order_price = float(key['price'])
                    new_price = new_order_price * 1.007267


                print('The Trade is Settle: ' + str(key['settled']))

                if key['settled'] == True:



                    order = {'price': str(round(new_price, 2)), 'size': key['size'], 'side': new_order_side,
                             'product_id': key['product_id']}

                    print("we need to execute this new order:")

                    print(order)
                    # new_trade = requests.post(order)

                    r = requests.post(api_url + '/orders', json=order, auth=auth)

                    print r.json()



                    last_fill_dealt_with2 = key['order_id']

                    if run_once == 0:
                        # last_fill_dealt_with = last_fill_dealt_with2

                        last_order_file_handle2 = open('GDAX/last_order_id_processed.txt', 'w')

                        last_order_file_handle2.write(str(last_fill_dealt_with2))

                        print(str(last_fill_dealt_with2))
                        last_order_file_handle2.close()
                        run_once = 1
                    break

    time.sleep(10)
