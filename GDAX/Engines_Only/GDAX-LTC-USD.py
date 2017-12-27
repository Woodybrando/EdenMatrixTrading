#!/usr/bin/env python

# Requires python-requests. Install with pip:
#
#   pip install requests
#
# or, with easy-install:
#
#   easy_install requests
#
#
#INDEX
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#



import json, hmac, hashlib, time, requests, base64, pickle
from requests.auth import AuthBase
from colorama import Fore, Back



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


f = open( "/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/config_GDAX_DONT_UPLOAD.json" , "rb" )
GDAX_config = json.load(f)
f.close()

#api_url = 'https://api-public.sandbox.gdax.com'
api_url = 'https://api.gdax.com'
GDAX_phrase = GDAX_config["GDAX_PASSPHRASE"]
GDAX_key = GDAX_config["GDAX_API_KEY"]
GDAX_secret = GDAX_config["GDAX_API_SECRET"]

auth = CoinbaseExchangeAuth( GDAX_key, GDAX_secret, GDAX_phrase)

a = 'LTC-USD'
b = 'LTC-BTC'
c = 'BTC-USD'

A = a
B = b
C = c

marketPair = a

from pprint import pprint

with open('/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/retraceDict-'
                  + marketPair + '.txt', 'r') as f:
    matrixDict = eval(f.read())

matrixVs = json.load(open('/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/'
                          'GDAX_matrix_variable_save-' + marketPair + '.txt'))

print("Market Pair is: " + str(matrixVs['Market Pair']))

Product_id = matrixVs['Market Pair']
marketPast = matrixVs['Market Price']
marketDec = matrixVs['marketDec']

isTrue = 1
newSide = 'none'
newPrice = '0'

while isTrue == 1:

    print("Entering Prime Loop")

    last_fill_file_handleE = open(
        '/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/last_order_id_processed-'
        + marketPair + '.txt', 'r+')
    last_fill_dealt_withE = last_fill_file_handleE.readline()
    print('this is the last ' + marketPair + ' order_id dealt with ' + last_fill_dealt_withE)
    last_fill_file_handleE.close()

    last_order_dealt_withN = last_fill_dealt_withE

    requestFills = requests.get(
        api_url + '/fills?cb-before=' + str(last_fill_dealt_withE) + '&product_id=' + marketPair, auth=auth)

    print(marketPair + ' Fills Request status code is ' + str(requestFills.status_code))

    if requestFills.status_code != 200:
        reconCount = 0
        while reconCount < 20:
            requestFills = requests.get(
            api_url + '/fills?cb-before=' + str(last_fill_dealt_withE) + '&product_id=' + marketPair, auth=auth)
            time.sleep(3)
            reconCount = reconCount + 1
            if requestFills.status_code == 200:
                count = 21

    jump = requestFills.json()


    print(jump)

    if jump[0]['order_id'] == str(last_fill_dealt_withE):

        print("This prints when we have an order ID match")

        marketPr = requests.get(api_url + '/products/' + marketPair + '/ticker')

        time.sleep(1)

        print(marketPr.status_code)

        if marketPr.status_code != 200:
            reconCount = 0
            while reconCount < 20:
                marketPr = requests.get(
                    api_url + '/products/' + marketPair + '/ticker')
                time.sleep(2)
                reconCount = reconCount + 1
                print(marketPr.status_code)
                if marketPr.status_code == 200:
                    reconCount = 21

        jsonPrice = marketPr.json()
        marketPr = float(jsonPrice['ask'])
        marketP = round(marketPr, marketDec)

        matrixVs['Market Price'] = marketP

        if marketP > marketPast:
            print(Fore.MAGENTA + 'No ' + marketPair + ' trades, hold tight, market is '
                  + Fore.GREEN + str(marketP) + Fore.CYAN
                  + ' ALL IS GOOD, ALL IS PROTECTED, ALL IN GOOD TIME' + Fore.WHITE)

        elif marketP == marketPast:
            print(Fore.MAGENTA + 'No ' + marketPair + ' trades, hold tight, market is '
                  + Fore.RESET + str(marketP) + Fore.CYAN
                  + ' ALL IS GOOD, ALL IS PROTECTED, ALL IN GOOD TIME' + Fore.WHITE)

        elif marketP < marketPast:
            print(Fore.MAGENTA + 'No ' + marketPair + ' trades, hold tight, market is '
                  + Fore.RED + str(marketP) + Fore.CYAN
                  + ' ALL IS GOOD, ALL IS PROTECTED, ALL IN GOOD TIME' + Fore.WHITE)

        marketPast = marketP

        time.sleep(5)

    elif jump[0]['order_id'] != str(last_fill_dealt_withE):

        print('A new order needs to be place!')

        jumpCount = 0

        while jump[jumpCount]['order_id'] != str(last_fill_dealt_withE):

            fill = jump[jumpCount]

            print('This is number ' + str(jumpCount) + ' through the jump loop')

            print('This is the current order id:')
            print(jump[jumpCount]['order_id'])

            print('This is the old order_id:')
            print(str(last_fill_dealt_withE))

            if jumpCount == 0:
                last_order_dealt_withN = jump[jumpCount]['order_id']

                print('last_order_dealt_withN just got set to:')
                print(last_order_dealt_withN)

                last_order_file_handle3 = open(
                '/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/last_order_id_processed-'
                + marketPair + '.txt',
                'w')

                last_order_file_handle3.write(last_order_dealt_withN)

                last_order_file_handle3.close()

                print('last_order_id_processed-' + marketPair + '.txt just got set to last_order_dealt_withN:')
                print(last_order_dealt_withN)

                print('Previous last_order_id_processed-' + marketPair + '.txt aka str(last_fill_dealt_withE) was:')

                print(str(last_fill_dealt_withE))

            if str(fill['order_id']) != str(last_fill_dealt_withE):

                print("New order_id is:")
                print[str(fill['order_id'])]
                print('Old order_id aka str(last_fill_dealt_withE) is:')
                print[str(last_fill_dealt_withE)]

                #figure out how to print the fill index here

                print('this is the fill:')
                pprint(fill)

                eSize = fill['size']
                Product_id = fill['product_id']
                lastFill = fill['order_id']

                if fill['side'] == 'buy':
                    priceCheck = (fill['price'] + ' buy')
                    newSide = 'sell'

                elif fill['side'] == 'sell':
                    priceCheck = (fill['price'] + ' sell')
                    newSide = 'buy'

                print("This is the matrixDict")
                pprint(matrixDict)

                roundFill = round(float(fill['price']), marketDec)
                dictPrice = str(roundFill)
                print("This is the dictPrice")
                print(dictPrice)
                stringFill = str(dictPrice)

                mdictKey = dictPrice + " " + fill['side']

                print("This is mdictKey")
                print(str(mdictKey))

                floatPrice = float(fill['price'])
                roundPrice = round(floatPrice , 2)

                newKey = str(roundPrice) + " " + fill['side']
                newPrice = matrixDict[mdictKey]

                strPeg = fill['price']

                pegDollar, pCode = strPeg.split('.')

                iDollar = int(pegDollar)

                iCode = int(pCode)

                if iCode == 98:
                    if newSide == 'buy':
                        iDollar = iDollar - 2
                        newPrice = iDollar + iCode

                    elif newSide == 'sell':
                        iDollar = iDollar + 2
                        newPrice = iDollar + iCode

                if iCode == 45:
                    if newSide == 'buy':
                        iDollar = iDollar - 5
                        newPrice = iDollar + iCode

                    if newSide == 'sell':
                        iDollar = iDollar + 5
                        newPrice = iDollar + iCode

                print("This is the new price")
                print(str(newPrice))

                #pprint(newPrice)

                engineOrder = {'side': newSide, 'size': eSize, 'price': newPrice, 'product_id': Product_id}

                print("This is the new order:")
                pprint(engineOrder)

                print("This is the order_id of the loops current fill:")
                print(fill['order_id'])

                print("Updated orderID is lastFill:")
                print(lastFill)

                print("File Saved orderID is str(last_fill_dealt_withE):")
                print(str(last_fill_dealt_withE))

                time.sleep(2)

                r = requests.post(api_url + '/orders', json=engineOrder, auth=auth)

                print("Order Status code is " + str(r.status_code))

                if r.status_code != 200:
                    reconCount = 0
                    while reconCount < 20:

                        r = requests.post(
                            api_url + '/orders', json=engineOrder, auth=auth)
                        time.sleep(2)
                        reconCount = reconCount + 1
                        if requestFills.status_code == 200:
                            count = 21

                time.sleep(1)

                orderResponse = r.json()

                #print("This is the order response default print")
                #print(orderResponse)

                print('This is the order response pretty print')
                pprint(orderResponse)

                jumpCount = jumpCount + 1

        time.sleep(5)

        if x is False:
            print('Big loop break')
            break