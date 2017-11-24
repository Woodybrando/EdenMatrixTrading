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



f = open( "/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/config_GDAX_DONT_UPLOAD.json" , "rb" )
GDAX_config = json.load(f)
f.close()


api_url = 'https://api.gdax.com'
#api_url = 'https://api-public.sandbox.gdax.com'


GDAX_phrase = GDAX_config["GDAX_PASSPHRASE"]
GDAX_key = GDAX_config["GDAX_API_KEY"]
GDAX_secret = GDAX_config["GDAX_API_SECRET"]


auth = CoinbaseExchangeAuth( GDAX_key, GDAX_secret, GDAX_phrase)


order = {}
loopit = True

#run_once = 0

LTC_USD = 'LTC-USD'

LTC_BTC = 'LTC-BTC'

BTC_USD = 'BTC-USD'


a = LTC_USD
A = LTC_USD

b = LTC_BTC
B = LTC_BTC

c = BTC_USD
C = BTC_USD

x = 0

y = 1

marketPair = input("Enter the letter of the market pair u want to trade in? a. LTC_USD b. LTC_BTC c. BTC_USD?")

if marketPair == a:
    marketDec = 2
elif marketPair == b:
    marketDec = 6
elif marketPair == c:
    marketDec = 2


# Add a way to set what entry point u want to start your matrix say if market is 75.5
# and u want to start only if price = 73



marketPr = {}

howPrice = input("Do u want to x. enter the market price or y. ask GDAX? x or y?")

if howPrice == x:
    marketP = input("What is the current market price?")



elif howPrice == y:
    marketPr = requests.get(api_url + '/products/LTC-USD/ticker')
    jsonPrice = marketPr.json()
    print(jsonPrice['ask'])
    marketPr = float(jsonPrice['ask'])
    marketP = round(marketPr, 2)

#requests.post(api_url + '/orders', json=order, auth=auth)

initInv = input("How much do you want to invest, and by invest I mean how much can u stand to lose???")


aboveInv = initInv/2

print("Above Investment: " + str(aboveInv))



aboveFee = aboveInv * .003

upperBuy = aboveInv - aboveFee

aboveInv = upperBuy

print("Upper Cost minus Fee " + str(upperBuy))


aboveCoins = aboveInv/marketP

print( "Above Coins: " + str(aboveCoins))

# turn this on as a question in the future
resolution = 25

aboveVol = round(aboveCoins/(resolution - 1), 4)

print("Above Coin Volume = " + str(aboveVol))

belowBuys = initInv - aboveInv

print("Below Investment: " + str(belowBuys))

unroundVal = belowBuys/(resolution - 1)

belowVal = round(unroundVal, 4)

print("Below Value Per Peg: " + str(belowVal))


marketTop = marketP * 1.12

print("Market Top " + str(marketTop))



marketBottom = .92 * marketP

print("Market Bottom " +  str(marketBottom))

marketUpper = marketP * 1.002
marketLower = marketP * .998

print("MarketUpper is " + str(marketUpper))
print("MarketLower is " + str(marketLower))


upperSpread = (marketTop - marketUpper) / (resolution - 1)
lowerSpread = (marketLower - marketBottom) / (resolution - 1)

print("Lower Spread " + str(lowerSpread))

peg = 0
number = 0
list = []
matrix = []
upperMatrix = []
lowerMatrix = []
countOrder = {}

count = resolution * 2 - 1

pegMakerU = marketP
pegMakerL = marketP

lNumber = 24
mNumber = 25
uNumber = 26

print("Count is " + str(count))

print("Current Market Price: " + str(marketPr))

while count > -1:

    peg = pegMakerU + upperSpread

    #print("Count is " + str(count))
    #print("Peg is " + str(peg))

    if count > resolution:

        volume = aboveVol

        rPeg = round(peg, marketDec)

        strPeg = str(rPeg)

        pegDollar, pCode = strPeg.split('.')

        iDollar = int(pegDollar)

        iCode = int(pCode)

        if iCode == 98:
            rPeggle = .97
            rPeg = iDollar + rPeggle

        if iCode == 45:
            rPeggle = .44
            rPeg = iDollar + rPeggle

        list = uNumber, rPeg, round(volume, 4)
        matrix.append(list)
        upperMatrix.append(list)
        pegMakerU = peg
        uNumber = uNumber + 1

    elif count == 25:
        peg = marketP
        rPeg = round(peg, 2)
        volume = aboveVol
        number = mNumber
        list = number, rPeg, round(volume, 4)
        matrix.append(list)

    elif count < resolution:
        peg = pegMakerL - lowerSpread

        if peg >= (marketBottom):

            belowVol = belowVal / peg
            volume = belowVol

            rPeg = round(peg, marketDec)

            strPeg = str(rPeg)

            pegDollar, pCode = strPeg.split('.')

            iDollar = int(pegDollar)

            iCode = int(pCode)

            if iCode == 98:
                rPeggle = .97
                rPeg = iDollar + rPeggle

            if iCode == 45:
                rPeggle = .44
                rPeg = iDollar + rPeggle

            list = lNumber, rPeg, round(volume, 4)
            matrix.append(list)
            lowerMatrix.append(list)
            pegMakerL = pegMakerL - lowerSpread
            lNumber = lNumber - 1



    # print(number, rPeg, rVol)

    count = count - 1



matrix.sort(key=lambda x: x[1])


print(matrix)
print(len(matrix))

print(upperMatrix)
print(len(upperMatrix))

print(lowerMatrix)
print(len(lowerMatrix))


'''
# To get the peg value printed uncomment this section

for line in matrix:

    pegValue2 = line[1] * line[2]
    print(round(pegValue2, 3))
    
print("Sum of row Values " + str(sum(rowVal)))
'''


totalInvestment = [ sum(x) for x in zip(*matrix) ]
totalUpperInvestment = [ sum(x) for x in zip(*upperMatrix) ]
totalLowerInvestment = [ sum(x) for x in zip(*lowerMatrix) ]

print("Total Upper Investment in Coins? " + str(totalUpperInvestment[2]))
#totalInvestment = sum(matrix)

upperCost = totalUpperInvestment[2] * marketP

print("Upper coin cost " + str(upperCost) )


sumLower = []

for line in lowerMatrix:
    pegVal = line[1] * line[2]
    rPegVal = round(pegVal, 3)
    sumLower.append(rPegVal)

lowerValAdd = sum(sumLower)

print(sumLower)

print("Lower buys total cost " + str(lowerValAdd))

totalMatrixCost = upperCost + lowerValAdd

print("Total Matrix Cost " + str(totalMatrixCost))



#print("Total Coin Cost: " + str(upperCost + lowerCost))

y = 0
n = 1
upperPegOrder = {}

exitAns = input("Do you want to exit? y or n?")

if exitAns == y:
    exit()

#for line in matrix:

buyAbove = input("Do you want to buy your above matrix now? y or n?")

if buyAbove == y:

    marketOrder = str(round(aboveInv, 2))
    print(marketOrder)

    rAboveCoins = str(round(aboveCoins, 3))

    buyNowAns = input(
        "Does that number look right, aka you will buy " + rAboveCoins + " " + str(marketPair)
        + " @ the current market price " + str(marketP)
        + " if you say yes? y or n?")

    if buyNowAns == y:
        aboveOrder = {'type': 'market', 'funds': marketOrder, 'product_id': str(marketPair), 'side': 'buy'}

        s = requests.post(api_url + '/orders', json=aboveOrder, auth=auth)

        print(s.json())



buildUpper = input("Do you want to build your upper matrix now? y or no?")

if buildUpper == n:
    exit()



elif buildUpper == y:

    for line in upperMatrix:
        upperSide = 'sell'
        upperVol = str(aboveVol)
        upperPeg = str(line[1])
        upperPegOrder = {'side': upperSide, 'price': upperPeg, 'size': upperVol, 'product_id': str(marketPair)}
        t = requests.post(api_url + '/orders', json=upperPegOrder, auth=auth)
        print(t.json())


exit()

for line in matrix:
    while line[1] > marketBottom:
        if line[1] >= marketUpper:
            side = 'sell'
        elif abs(line[1] - marketP) < abs(marketUpper - marketLower):
            side = 0
        elif line[1] <= marketLower:
            side = 'buy'

    if side != 0:
        matrixOrder = { 'price': str(line[1]), 'size': str(line[2]), 'side': str(side), 'product_id': str(marketPair)}

        print(order)

        r = requests.post(api_url + '/orders', json=matrixOrder, auth=auth)





y = 0
n = 1

exitAns = input("Do you want to exit? y or n?")

if exitAns == y:
    exit()
elif exitAns == n:
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



