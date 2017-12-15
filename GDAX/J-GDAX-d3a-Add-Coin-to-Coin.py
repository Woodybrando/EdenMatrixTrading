# Requires python-requests. Install with pip:
#
#   pip install requests
#
# or, with easy-install:
#
#   easy_install requests

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


api_url = 'https://api.gdax.com'
#api_url = 'https://api-public.sandbox.gdax.com'


GDAX_phrase = GDAX_config["GDAX_PASSPHRASE"]
GDAX_key = GDAX_config["GDAX_API_KEY"]
GDAX_secret = GDAX_config["GDAX_API_SECRET"]


auth = CoinbaseExchangeAuth( GDAX_key, GDAX_secret, GDAX_phrase)


order = {}
matrix_dict = {}
pillar_dict = {}
retrace_dict = {}
pillars_retrace_dict = {}
loopit = True

#run_once = 0

LTC_USD = 'LTC-USD'



LTC_BTC = 'LTC-BTC'

BTC_USD = 'BTC-USD'


a = LTC_USD
A = a

b = LTC_BTC
B = b

c = BTC_USD
C = c

x = 0
X = x

y = 1
Y = y

n = 2
N = n

m = 1
M = m


s = 2
S = s

e = 3
E = e


doWhat = input("Do you want to m. build a matrix file s. buy and set up your matrix or e. activate the rebuy engine? \n"
               "type m or s or e?")

if doWhat == m:

    marketPair = input("Enter the letter of the market pair u want to trade in? a. LTC_USD b. LTC_BTC c. BTC_USD?")

    print(str(b))

    if marketPair == a:
        marketDec = 2
        matrix_dict['marketDec'] = marketDec
        matrix_dict['Market Pair'] = 'LTC-USD'
        print('Market pair is ' + matrix_dict['Market Pair'])

    elif marketPair == b:
        marketDec = 5
        matrix_dict['marketDec'] = marketDec
        matrix_dict['Market Pair'] = 'LTC-BTC'
        print('You pressed b')
        print('Market pair is ' + matrix_dict['Market Pair'])

    elif marketPair == c:
        marketDec = 2
        matrix_dict['marketDec'] = marketDec
        matrix_dict['Market Pair'] = 'BTC-USD'
        print('Market pair is ' + matrix_dict['Market Pair'])

    # Add a way to set what entry point u want to start your matrix say if market is 75.5
    # and u want to start only if price = 73

    marketPr = {}

    howPrice = input("Do u want to x. enter the market price or y. ask GDAX? x or y?")

    if howPrice == x:
        marketP = input("What is the current market price?")

    elif howPrice == y:
        marketPr = requests.get(api_url + '/products/' + matrix_dict['Market Pair'] + '/ticker')
        marketLTC = requests.get(api_url + '/products/LTC-USD/ticker')
        marketBTC = requests.get(api_url + '/products/BTC-USD/ticker')

        print(str(marketPr))

        time.sleep(1)

        print(marketPr.status_code)

        if marketPr.status_code != 200:
            reconCount = 0
            while reconCount < 20:
                marketPr = requests.get(
                    api_url + '/products/' + matrix_dict['Market Pair'] + '/ticker')
                marketLTC = requests.get(api_url + '/products/LTC-USD/ticker')
                marketBTC = requests.get(api_url + '/products/BTC-USD/ticker')
                time.sleep(2)
                reconCount = reconCount + 1
                print(marketPr.status_code)
                if marketPr.status_code == 200:
                    count = 21

        jsonPrice = marketPr.json()
        jsonLTC = marketLTC.json()
        jsonBTC = marketBTC.json()

        print('LTC/BTC Market Price is ' + jsonPrice['ask'])
        marketPr = float(jsonPrice['ask'])
        marketP = round(marketPr, marketDec)

        print('LTC Market Price is ' + jsonLTC['ask'])
        marketLTC = float(jsonLTC['ask'])
        marketLTC = round(marketLTC, 2)

        print('BTC Market Price is ' + jsonBTC['ask'])
        marketBTC = float(jsonBTC['ask'])
        marketBTC = round(marketBTC, 2)

    #requests.post(api_url + '/orders', json=order, auth=auth)

    matrix_dict['Market Price'] = marketP
    matrix_dict['LTC Price'] = marketLTC
    matrix_dict['BTC Price'] = marketBTC

    if marketPair == a:
        aboveCoin = marketP
        belowCoin = marketP

    if marketPair == b:
        aboveCoin = matrix_dict['LTC Price']
        belowCoin = matrix_dict['BTC Price']

    if marketPair == c:
        aboveCoin = marketP
        belowCoin = marketP

    initInv = input("How much do you want to invest aka amount u can lose and still pay all your bills? \n"
                    "i.e. 1000 or 5273")

    investmentFactor = input("How do you want to divide your investment into your above/below matrices ? \n"
                    "i.e. enter .5 to put 50% above and 50% below \n"
                    "or .2 for 20% above 80% below")

    aboveInv = initInv * investmentFactor

    matrix_dict['Above Investment'] = aboveInv

    print("Above Investment: " + str(aboveInv))

    aboveFee = aboveInv * .003

    matrix_dict['Above Fee'] = aboveFee

    upperBuy = aboveInv - aboveFee

    matrix_dict['Above Buy'] = upperBuy

    lowerBuy = initInv - aboveInv

    matrix_dict['Below Buy'] = lowerBuy

    print("Upper Cost minus Fee " + str(upperBuy))

    aboveCoins = aboveInv/aboveCoin

    matrix_dict['Above Coins'] = aboveCoins

    print( "Above Coins: " + str(aboveCoins))

    # turn this on as a question in the future

    resolutionAbove = input("What resolution do you want to use in your upper matrix?\n"
                            "i.e. 25 is twenty five sell pegs one spread from the last\n"
                            "integers only")

    resolutionBelow = input("What resolution do you want to use in your lower matrix?\n"
                            "i.e. 5 is 5 pillars below which will be of a greater volume vs\n"
                            "25 that are at smaller volume\n"
                            "integers only")

    matrix_dict['Resolution Above'] = resolutionAbove
    matrix_dict['Resolution Below'] = resolutionBelow

    aboveVol = round(aboveCoins/resolutionAbove, 4)

    matrix_dict['Above Volume'] = aboveVol

    print("Above Coin Volume = " + str(aboveVol))

    abovePegValue = upperBuy/resolutionAbove
    lowerPegValue = lowerBuy/resolutionBelow

    matrix_dict['Above Peg Value'] = abovePegValue
    matrix_dict['Below Peg Value'] = lowerPegValue

    print("abovePegValue is " + str(abovePegValue))
    print("belowPegValue is " + str(lowerPegValue))

    belowBuys = initInv - aboveInv

    matrix_dict['Below Buys'] = belowBuys

    print("Below Investment: " + str(belowBuys))

    unroundVal = belowBuys/resolutionBelow

    matrix_dict['Unrounded Below Peg Value'] = unroundVal

    belowVal = round(unroundVal, 4)

    coinBelow = marketLTC/belowVal

    matrix_dict['Below Peg Value'] = belowVal
    matrix_dict['Coin Below'] = coinBelow

    print("Below Value Per Peg: " + str(belowVal))
    print("Below Value Per Peg: " + str(coinBelow))

    h = 1
    H = h
    p = 2
    P = p
    m = 3
    M = m

    topAns = input("Do you want to set the matrix top and bottom by h. hand or by p. multipliers? h or m?")

    if topAns == h:

        marketTop = input("What is the top price for your matrix? ie. 177.87 or .00023 etc")

        marketBottom = input("What is the bottom price for your matrix? i.e. 5479 or 20.23 or .0071")

    elif topAns == m:

        topFactor =  input("What multiplier do you want to use to create your matrix top? i.e. one point two times is: 1.2")

        marketTop = marketP * topFactor

        bottomFactor = input("What multiplier do you want to use to create your matrix bottom? \n "
                             "i.e. .2 would set a lower matrix range twenty percent below \n "
                             "the starting market or peg price so if market is $100 a .2 multiplier\n"
                             "would set buys from market down to $80 or 20 percent down from market.")

        marketBottom = marketP - (bottomFactor * marketP)

    matrix_dict['Market Top'] = marketTop
    matrix_dict['Market Bottom'] = marketBottom

    print("Market Top " + str(marketTop))
    print("Market Bottom " +  str(marketBottom))


    upperSpread = (marketTop - marketP) / resolutionAbove
    lowerSpread = (marketP - marketBottom) / resolutionBelow

    matrix_dict['Upper Spread'] = upperSpread
    matrix_dict['Lower Spread'] = lowerSpread

    print("Upper Spread " + str(upperSpread))
    print("Lower Spread " + str(lowerSpread))

    peg = 0
    number = 0
    list = []
    matrix = []
    upperMatrix = []
    lowerMatrix = []
    countOrder = {}

    resolution  = resolutionAbove + resolutionBelow + 1

    matrix_dict['Total Resolution'] = resolution

    count = resolutionAbove + resolutionBelow + 1

    pegMakerU = marketP
    pegMakerL = marketP

    lNumber = resolutionBelow - 1
    mNumber = resolutionBelow
    uNumber = resolutionBelow + 1

    lowerCounter = resolutionBelow - 1

    print('lNumber is ' + str(lNumber))
    print('mNumber is ' + str(mNumber))
    print('uNumber is ' + str(uNumber))
    print("Count is " + str(count))
    print("Current Market Price: " + str(marketPr))

    counter = 0
    peg = marketP

    while counter < count:

        if counter > mNumber:

            peg = peg + upperSpread

            volume = aboveVol

            if marketPair != b:

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
                peg = rPeg

            peg = round(peg, marketDec)
            list = counter, peg, round(volume, 4)
            matrix.append(list)
            upperMatrix.append(list)
            pegMakerU = peg

            print('Counter is ' + str(counter))
            print('pegMakerU is ' + str(pegMakerU))

            uNumber = uNumber + 1

        elif counter == mNumber:
            peg = marketP
            volume = aboveVol
            list = counter, peg, round(volume, 4)
            matrix.append(list)

            print('Counter is ' + str(counter))

        elif counter < mNumber:
            peg = pegMakerL - lowerSpread
            volume = peg / belowVal

            if marketPair == b:
                nonFiatVal = lowerPegValue / marketBTC
                volume = nonFiatVal/peg

            if marketPair != b:

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

                peg = rPeg

            peg = round(peg, marketDec)
            list = lowerCounter , peg, round(volume, 4)
            matrix.append(list)
            lowerMatrix.append(list)
            print('pegMakerL is ' + str(pegMakerL))
            print('Counter is ' + str(counter))
            print('lowerCounter is ' + str(lowerCounter))

            pegMakerL = pegMakerL - lowerSpread
            lowerCounter = lowerCounter - 1




        counter = counter + 1

    matrix.sort(key=lambda x: x[1])

    for line6 in matrix:
        if line6[0] == 0:
            print("This is the matrix peg price: " + str(line6[1]))
            retrace_dict[str(line6[1]) + ' buy'] = matrix[(line6[0] + 1)]
            print("Market hit your matrix bottom")
            print(line6)

        elif line6[0] == resolution:
            print("This is the matrix peg price: " + str(line6[1]))
            retrace_dict[str(line6[1]) + ' sell'] = matrix[(line6[0] - 1)][1]
            print("Market hit your matrix top")
            print(line6)
            print("Matrix Resolution is " + str(resolution))

        else:
            print("This is the matrix peg price: " + str(line6[1]))
            print(line6)
            retrace_dict[str(line6[1]) + ' buy'] = matrix[(line6[0] + 1)][1]
            retrace_dict[str(line6[1]) + ' sell'] = matrix[(line6[0] - 1)][1]

    print(matrix)

    saveMatrix = input("Do you want to save the matrices to a local files? y or n")
    if saveMatrix == y:

        with open('/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/matrixGDAX.pickle', 'wb') as handle:
            pickle.dump(matrix, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open('/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/upperMatrixGDAX.pickle', 'wb') as handle:
            pickle.dump(upperMatrix, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open('/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/lowerMatrixGDAX.pickle', 'wb') as handle:
            pickle.dump(lowerMatrix, handle, protocol=pickle.HIGHEST_PROTOCOL)

    print(len(matrix))
    print(upperMatrix)
    print(len(upperMatrix))
    print(lowerMatrix)
    print(len(lowerMatrix))

    totalInvestment = [ sum(x) for x in zip(*matrix) ]
    totalUpperInvestment = [ sum(x) for x in zip(*upperMatrix) ]
    totalLowerInvestment = [ sum(x) for x in zip(*lowerMatrix) ]

    print("Total Upper Investment in Coins? " + str(totalUpperInvestment[2]))

    upperCost = totalUpperInvestment[2] * marketP

    print("Upper coin cost " + str(upperCost) )

    sumLower = []

    for line in lowerMatrix:
        pegVal = line[1] * line[2]
        rPegVal = round(pegVal, 3)
        sumLower.append(rPegVal)

    lowerValAdd = sum(sumLower)

    print("Peg Values:")
    print(sumLower)

    print("Lower buys total cost " + str(lowerValAdd))

    totalMatrixCost = upperCost + lowerValAdd

    print("Total Matrix Cost " + str(totalMatrixCost))

    pillarAsk = input("Do you want to add a matrix of pillars? y or n?")

    if pillarAsk == y:

        pillarBuy = input("How much do you want to invest in the pillars? i.e. 200, 1.20, .003?")

        #Add an account check here to make sure there is enough

        investmentFactorP = input(
            "How do u want to divide you pillar buy above/below? .5 is 50/50, .2 is .2 above .8 below?")

        aboveInvP = pillarBuy * investmentFactorP

        pillar_dict['Pillar Above Investment'] = aboveInvP

        print("Pillar Above Investment: " + str(pillar_dict['Pillar Above Investment']))

        aboveFeeP = aboveInvP * .003

        pillar_dict['Pillar Above Fee'] = aboveFeeP

        upperBuyP = aboveInvP - aboveFeeP

        pillar_dict['Pillar Above Buy'] = upperBuyP

        lowerBuyP = pillarBuy - aboveInvP

        pillar_dict['Pillar Below Buy'] = lowerBuyP

        print("Pillar Upper Cost minus Fee " + str(upperBuyP))

        aboveCoinsP = aboveInvP / marketP

        pillar_dict['Pillar Above Coins'] = aboveCoinsP

        print("Pillar Above Coins: " + str(aboveCoinsP))

        pillarTopAns = input("Do you want to enter pillar top and bottom h. by hand or m. or by multiplier? h or m?")

        if pillarTopAns == h:

            pillarTop = input("What is the top price for your pillar matrix? ie. 177.87 or .00023 etc")
            pillarBottom = input("What is the bottom price for your matrix? i.e. 5479 or 20.23 or .0071")

        elif pillarTopAns == m:

            topFactorP = input(
                "What multiplier do you want to use to create your matrix top? i.e. one point two times is: 1.2")
            pillarTop = marketP * topFactorP

            bottomFactorP = input("What multiplier do you want to use to create your matrix bottom? \n "
                                 "i.e. .2 would set a lower matrix range twenty percent below \n "
                                 "the starting market or peg price so if market is $100 a .2 multiplier\n"
                                 "would set buys from market down to $80 or 20 percent down from market.")
            pillarBottom = marketP - (bottomFactorP * marketP)

        pillar_dict['Top Pillar'] = pillarTop
        pillar_dict['Bottom Pillar'] = pillarBottom

        print("Market Top " + str(pillarTop))
        print("Market Bottom " + str(pillarBottom))

        resolutionAboveP = input("What is your above resolution? # of pillars above, i.e. 5, 10, 15?")
        resolutionBelowP = input("What is your below resolution? # of pillars above, i.e. 5, 10, 15?")

        upperSpreadP = (pillarTop - marketP) / (resolutionAboveP)
        lowerSpreadP = (marketP - pillarBottom) / (resolutionBelowP)

        pillar_dict['Pillar Upper Spread'] = upperSpreadP
        pillar_dict['Pillar Lower Spread'] = lowerSpreadP

        print("Pillar Upper Spread " + str(upperSpreadP))
        print("Pillar Lower Spread " + str(lowerSpreadP))

        aboveVolP = aboveCoinsP / resolutionAboveP
        belowValP = lowerBuyP / resolutionBelowP

        pegP = 0
        numberP = 0
        listP = []
        pillars = []
        upperPillars = []
        lowerPillars = []
        countOrderP = {}

        resolutionP = resolutionAboveP + resolutionBelowP + 1

        pillar_dict['Total Resolution'] = resolutionP

        countP = resolutionAboveP + resolutionBelowP + 1
        pillarMakerU = marketP
        pillarMakerL = marketP
        mNumberP = resolutionBelowP + 1

        print("Count is " + str(countP))

        print("Current Market Price: " + str(marketP))

        while countP >= 0:

            pegP = pillarMakerU + upperSpreadP

            if countP > mNumberP:

                volumeP = aboveVolP

                rPegP = round(pegP, marketDec)

                strPegP = str(rPegP)

                pegDollarP, pCodeP = strPegP.split('.')

                iDollarP = int(pegDollarP)

                iCodeP = int(pCodeP)

                if iCodeP < 35:
                    rPeggleP = .98
                    iDollarP = iDollarP - 1
                    rPegP = iDollarP + rPeggleP

                elif iCodeP > 88:
                    rPeggleP = .98
                    rPegP = iDollarP + rPeggleP

                if iCodeP >= 35 <= 87:
                    rPeggleP = .48
                    rPegP = iDollarP + rPeggleP

                listP = uNumberP, rPegP, round(volumeP, 4)
                pillars.append(listP)
                upperPillars.append(listP)
                pillarMakerU = pegP
                uNumberP = uNumberP + 1

            elif countP == mNumberP:
                pegP = marketP

                rPegP = round(pegP, marketDec)

                strPegP = str(rPegP)

                pegDollarP, pCodeP = strPegP.split('.')

                iDollarP = int(pegDollarP)

                iCodeP = int(pCodeP)

                if iCodeP < 35:
                    rPeggleP = .98
                    iDollarP = iDollarP - 1
                    rPegP = iDollarP + rPeggleP

                elif iCodeP > 88:
                    rPeggleP = .98
                    rPegP = iDollarP + rPeggleP

                if iCodeP >= 35 <= 87:
                    rPeggleP = .48
                    rPegP = iDollarP + rPeggleP

                volumeP = aboveVolP
                numberP = mNumberP
                listP = numberP, rPegP, round(volumeP, 4)
                pillars.append(listP)

            elif countP < mNumberP:
                pegP = pillarMakerL - lowerSpreadP

                if pegP >= (pillarBottom):

                    belowVolP = belowValP / pegP
                    volumeP = belowVolP

                    rPegP = round(pegP, marketDec)

                    strPegP = str(rPegP)

                    pegDollarP, pCodeP = strPegP.split('.')

                    iDollarP = int(pegDollarP)

                    iCodeP = int(pCodeP)

                    if iCodeP < 35:
                        rPeggleP = .98
                        iDollarP = iDollarP - 1
                        rPegP = iDollarP + rPeggleP

                    elif iCodeP > 88:
                        rPeggleP = .98
                        rPegP = iDollarP + rPeggleP

                    if iCodeP >= 35 <= 87:
                        rPeggleP = .48
                        rPegP = iDollarP + rPeggleP

                    listP = lNumberP, rPegP, round(volumeP, 4)
                    pillars.append(listP)
                    lowerMatrix.append(listP)
                    pillarMakerL = pillarMakerL - lowerSpreadP
                    lNumberP = lNumberP - 1

            countP = countP - 1
            print("Count is " + str(countP))

        pillars.sort(key=lambda x: x[1])

        for line6 in pillars:
            if line6[0] == 0:
                print("This is the matrix peg price: " + str(line6[1]))
                pillars_retrace_dict[str(line6[1]) + ' buy'] = pillars[(line6[0] + 1)]
                print("Market hit your bottom pillar")

            elif line6[0] == resolutionP:
                print("This is the matrix peg price: " + str(line6[1]))
                pillars_retrace_dict[str(line6[1]) + ' sell'] = pillars[(line6[0] - 1)][1]
                print("Market hit your top pillar")

            else:
                print("This is the pillar peg price: " + str(line6[1]))
                pillars_retrace_dict[str(line6[1]) + ' buy'] = pillars[(line6[0] + 1)][1]
                pillars_retrace_dict[str(line6[1]) + ' sell'] = pillars[(line6[0] - 1)][1]

        print(pillars)

        json.dump(pillars_retrace_dict, open(
            "/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/pillars_retraceDict.txt", 'w'))

    y = 0
    Y = y
    n = 1
    N = n
    upperPegOrder = {}

    saveVars = input("Do you want to save the variables from the matrix? y or n?")

    if saveVars == y:

        json.dump(matrix_dict, open(
            "/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/GDAX_matrix_variable_save.txt", 'w'))
        json.dump(retrace_dict, open(
            "/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/retraceDict.txt", 'w'))
        json.dump(pillar_dict, open(
            "/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/pillarDict.txt", 'w'))

    exitAns = input("Do you want to exit or set up a matrix? y or s?")

    if exitAns == y:
        exit()

    else:

        doWhat = s

elif doWhat == s:

    matrixVs = json.load(open("/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/GDAX_matrix_variable_save.txt"))

    print("Archived Market Price Saved Matrices were built on: " + str(matrixVs['Market Price']))

    marketPr = requests.get(api_url + '/products/LTC-USD/ticker')
    jsonPrice = marketPr.json()
    marketPr = float(jsonPrice['ask'])
    marketCurrent = round(marketPr, 2)

    print("Current Market Price: " + str(marketCurrent))

    print("Total Resolution: " + str(matrixVs['Total Resolution']))

    with open('/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/matrixGDAX.pickle', 'rb') as handle:
        matrixRead = pickle.load(handle)

    print("This is the matrix:")
    print(matrixRead)

    with open('/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/upperMatrixGDAX.pickle', 'rb') as handle:
        upperMatrixRead = pickle.load(handle)

    print("This is the upper matrix:")
    print(upperMatrixRead)

    with open('/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/lowerMatrixGDAX.pickle', 'rb') as handle:
        lowerMatrixRead = pickle.load(handle)

    print("This is the lower matrix:")
    print(lowerMatrixRead)

    marketP = matrixVs['Market Price']
    aboveInv = matrixVs['Above Investment']
    aboveCoins = matrixVs['Above Coins']
    aboveVol = matrixVs['Above Volume']
    marketPair = matrixVs['Market Price']
    lowerMatrix = matrixVs['Market Price']
    Product_id = matrixVs['Market Pair']

    buyAbove = input("Do you want to buy your above matrix now? y or n?")

    orderCount = 0

    if buyAbove == y:

        marketOrder = str(round(aboveInv, 2))
        print(marketOrder)

        rAboveCoins = str(round(aboveCoins, 3))

        buyNowAns = input(
            "Does that number look right, aka you will buy " + rAboveCoins + " " + str(marketPair)
            + " @ the current market price " + str(marketP)
            + " if you say yes? y or n?")

        if buyNowAns == y:
            aboveOrder = {'type': 'market', 'funds': marketOrder, 'product_id': Product_id, 'side': 'buy'}

            s = requests.post(api_url + '/orders', json=aboveOrder, auth=auth)

            print(s.json())

            last_order_file_handle = open('/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/last_order_id_processed.txt', 'r+')
            last_fill_dealt_withL = last_order_file_handle.readline()
            print('this is the last order_id dealt with ' + last_fill_dealt_withL)
            last_order_file_handle.close()

            e = requests.get(api_url + '/fills?cb-before=' + str(last_fill_dealt_withL) + '&product_id=LTC-USD', auth=auth)
            print(e.json())

            for key in e.json():
                wait = 0

                print('    this is the most recent order_id ' + key['order_id'])

                last_fill_dealt_with0 = key['order_id']
                last_order_file_handle0 = open('/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/last_order_id_processed.txt', 'w')
                last_order_file_handle0.write(str(last_fill_dealt_with0))
                print(str(last_fill_dealt_with0))
                last_order_file_handle0.close()
                break

    print(upperMatrixRead[0][1])

    buildUpper = input("Do you want to build your upper matrix now? y or no?")

    if buildUpper == y:

        for line in upperMatrixRead:
            upperSide = 'sell'
            upperVol = str(aboveVol)
            upperPeg = float(line[1])
            upperPegOrder = {'side': upperSide, 'price': upperPeg, 'size': upperVol, 'product_id': Product_id}
            t = requests.post(api_url + '/orders', json=upperPegOrder, auth=auth)
            print(t.json())


    buildLower = input("Do you want to build your lower matrix now? y or n?")

    if buildLower == y:

        for line2 in lowerMatrixRead:
            lowerSide = 'buy'
            lowerPeg = float(line2[1])
            lowerVol = float(line2[2])
            lowerPegOrder = {'side': lowerSide, 'price': lowerPeg, 'size': lowerVol, 'product_id': Product_id}
            u = requests.post(api_url + '/orders', json=lowerPegOrder, auth=auth)
            print(u.json())

elif doWhat == e:

    from pprint import pprint

    with open('/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/retraceDict.txt', 'r') as f:
        matrixDict = eval(f.read())

    matrixVs = json.load(open("/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/GDAX_matrix_variable_save.txt"))

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
            '/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/last_order_id_processed.txt', 'r+')
        last_fill_dealt_withE = last_fill_file_handleE.readline()
        print('this is the last order_id dealt with ' + last_fill_dealt_withE)
        last_fill_file_handleE.close()

        last_order_dealt_withN = last_fill_dealt_withE

        requestFills = requests.get(
            api_url + '/fills?cb-before=' + str(last_fill_dealt_withE) + '&product_id=LTC-USD', auth=auth)

        print("Fills Request status code is " + str(requestFills.status_code))

        if requestFills.status_code != 200:
            reconCount = 0
            while reconCount < 20:
                requestFills = requests.get(
                api_url + '/fills?cb-before=' + str(last_fill_dealt_withE) + '&product_id=LTC-USD', auth=auth)
                time.sleep(3)
                reconCount = reconCount + 1
                if requestFills.status_code == 200:
                    count = 21

        jump = requestFills.json()


        print(jump)

        if jump[0]['order_id'] == str(last_fill_dealt_withE):

            print("This prints when we have an order ID match")

            marketPr = requests.get(api_url + '/products/LTC-USD/ticker')

            time.sleep(1)

            print(marketPr.status_code)

            if marketPr.status_code != 200:
                reconCount = 0
                while reconCount < 20:
                    marketPr = requests.get(
                        api_url + '/products/LTC-USD/ticker')
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
                print(Fore.MAGENTA + "No trades, hold tight, market is " + Fore.GREEN + str(marketP) + Fore.CYAN
                      + " ALL IS GOOD, ALL IS PROTECTED, ALL IN GOOD TIME" + Fore.WHITE)

            elif marketP == marketPast:
                print(Fore.MAGENTA + "No trades, hold tight, market is " + Fore.RESET + str(marketP) + Fore.CYAN
                      + " ALL IS GOOD, ALL IS PROTECTED, ALL IN GOOD TIME" + Fore.WHITE)

            elif marketP < marketPast:
                print(Fore.MAGENTA + "No trades, hold tight, market is " + Fore.RED + str(marketP) + Fore.CYAN
                      + " ALL IS GOOD, ALL IS PROTECTED, ALL IN GOOD TIME" + Fore.WHITE)

            marketPast = marketP

            time.sleep(5)

        elif jump[0]['order_id'] != str(last_fill_dealt_withE):

            print("A new order needs to be place!")

            jumpCount = 0

            while jump[jumpCount]['order_id'] != str(last_fill_dealt_withE):

                fill = jump[jumpCount]

                print("This is number " + str(jumpCount) + " through the jump loop")

                print("This is the current order id:")
                print(jump[jumpCount]['order_id'])

                print("This is the old order_id:")
                print(str(last_fill_dealt_withE))

                if jumpCount == 0:
                    last_order_dealt_withN = jump[jumpCount]['order_id']

                    print("last_order_dealt_withN just got set to:")
                    print(last_order_dealt_withN)

                    last_order_file_handle3 = open(
                    '/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/last_order_id_processed.txt',
                    'w')

                    last_order_file_handle3.write(last_order_dealt_withN)

                    last_order_file_handle3.close()

                    print("last_order_id_processed.txt just got set to last_order_dealt_withN:")
                    print(last_order_dealt_withN)

                    print("Previous last_order_id_processed.txt aka str(last_fill_dealt_withE) was:")

                    print(str(last_fill_dealt_withE))

                if str(fill['order_id']) != str(last_fill_dealt_withE):

                    print("New order_id is:")
                    print[str(fill['order_id'])]
                    print("Old order_id aka str(last_fill_dealt_withE) is:")
                    print[str(last_fill_dealt_withE)]

                    #figure out how to print the fill index here

                    print("this is the fill:")
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

                    print("This is the order response pretty print")
                    pprint(orderResponse)

                    jumpCount = jumpCount + 1

            time.sleep(5)

            if x is False:
                print("Big loop break")
                break


'''
  File "/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/J-GDAX-d2a-New_Matrix_Engine.py", line 1014, in <module>
    newPrice = matrixDict[mdictKey]
KeyError: u'292.06 sell'

Traceback (most recent call last):
  File "/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/J-GDAX-d2a-New_Matrix_Engine.py", line 1014, in <module>
    newPrice = matrixDict[mdictKey]
KeyError: u'369.29 buy'

Traceback (most recent call last):
  File "/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/J-GDAX-d2a-New_Matrix_Engine.py", line 1014, in <module>
    newPrice = matrixDict[mdictKey]
KeyError: u'335.0 buy'

This prints when we have an order ID match
Traceback (most recent call last):
  File "/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/J-GDAX-d2a-New_Matrix_Engine.py", line 879, in <module>
    marketPr = requests.get(api_url + '/products/LTC-USD/ticker')
  File "/Library/Python/2.7/site-packages/requests/api.py", line 72, in get
    return request('get', url, params=params, **kwargs)
  File "/Library/Python/2.7/site-packages/requests/api.py", line 58, in request
    return session.request(method=method, url=url, **kwargs)
  File "/Library/Python/2.7/site-packages/requests/sessions.py", line 508, in request
    resp = self.send(prep, **send_kwargs)
  File "/Library/Python/2.7/site-packages/requests/sessions.py", line 618, in send
    r = adapter.send(request, **kwargs)
  File "/Library/Python/2.7/site-packages/requests/adapters.py", line 508, in send
    raise ConnectionError(e, request=request)
requests.exceptions.ConnectionError: HTTPSConnectionPool(host='api.gdax.com', port=443): Max retries exceeded with url: /products/LTC-USD/ticker (Caused by NewConnectionError('<urllib3.connection.VerifiedHTTPSConnection object at 0x10cc3c590>: Failed to establish a new connection: [Errno 8] nodename nor servname provided, or not known',))

Process finished with exit code 1

this is the last order_id dealt with 9a3d9a2f-e5bc-4430-a975-3f631e323c17
Traceback (most recent call last):
  File "/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/J-GDAX-d2a-New_Matrix_Engine.py", line 871, in <module>
    api_url + '/fills?cb-before=' + str(last_fill_dealt_withE) + '&product_id=LTC-USD', auth=auth)
  File "/Library/Python/2.7/site-packages/requests/api.py", line 72, in get
    return request('get', url, params=params, **kwargs)
  File "/Library/Python/2.7/site-packages/requests/api.py", line 58, in request
    return session.request(method=method, url=url, **kwargs)
  File "/Library/Python/2.7/site-packages/requests/sessions.py", line 508, in request
    resp = self.send(prep, **send_kwargs)
  File "/Library/Python/2.7/site-packages/requests/sessions.py", line 618, in send
    r = adapter.send(request, **kwargs)
  File "/Library/Python/2.7/site-packages/requests/adapters.py", line 490, in send
    raise ConnectionError(err, request=request)
requests.exceptions.ConnectionError: ('Connection aborted.', error(54, 'Connection reset by peer'))


'''