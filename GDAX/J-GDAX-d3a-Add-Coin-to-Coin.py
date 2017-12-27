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

order = {}
matrix_dict = {}
pillar_dict = {}
retrace_dict = {}
pillars_retrace_dict = {}
loopit = True

a = 'LTC-USD'
A = a

b = 'LTC-BTC'
B = b

c = 'BTC-USD'
C = c

i = 0
I = i

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
        marketLTC = requests.get(api_url + '/products/LTC-USD/ticker')
        marketBTC = requests.get(api_url + '/products/BTC-USD/ticker')

    elif howPrice == y:
        marketPr = requests.get(api_url + '/products/' + matrix_dict['Market Pair'] + '/ticker')
        marketLTC = requests.get(api_url + '/products/LTC-USD/ticker')
        marketBTC = requests.get(api_url + '/products/BTC-USD/ticker')

        print(str(marketPr))
        #print(marketPr.status_code)

        time.sleep(1)

        if marketPr.status_code != 200:
            reconCount = 0
            while reconCount < 20:
                marketPr = requests.get(
                    api_url + '/products/' + matrix_dict['Market Pair'] + '/ticker')

                time.sleep(2)
                reconCount = reconCount + 1
                print(marketPr.status_code)
                if marketPr.status_code == 200:
                    count = 21

        jsonPrice = marketPr.json()

        print('LTC/BTC Market Price is ' + jsonPrice['ask'])
        marketPr = float(jsonPrice['ask'])
        marketP = round(marketPr, marketDec)

    jsonLTC = marketLTC.json()
    jsonBTC = marketBTC.json()

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

    aboveCoins = aboveInv / marketLTC

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

    coinBelow = belowVal/marketLTC

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

    resolution  = resolutionAbove + resolutionBelow

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
    conStat = 0
    setStat = 0
    peg = marketP

    if marketPair == b:
        conStat = input("Do you want the volume to be the same or "
                        "to increase as the price goes away from the original market price? \n"
                        "s for same or i for increase? s or i?")
        if conStat == s:
            setStat = input("Set volume or have it set automatically?" 
                            "type s or a?")
            if setStat == s:
                setVolume = input("What volume do you want to set?")

    while counter < count:

        if counter > mNumber:

            peg = peg + upperSpread

            if conStat == i:
                nonFiatVal = abovePegValue / marketBTC
                print("NonFiatVal is:")
                print(nonFiatVal)
                volume = nonFiatVal / peg
                print("Volume for b is:")
                print(volume)

            if setStat == a:
                volume = aboveVol

            if setStat == s:
                volume = setVolume

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

            if conStat == i:
                volume = aboveVol

            if setStat == s:
                volume = setVolume

            if setStat == a:
                nonFiatVal = abovePegValue / marketBTC
                print("NonFiatVal is:")
                print(nonFiatVal)
                volume = nonFiatVal / peg
                print("Volume for b is:")
                print(volume)

            list = counter, peg, round(volume, 4)
            matrix.append(list)

            print('Counter is ' + str(counter))

        elif counter < mNumber:
            peg = pegMakerL - lowerSpread

            if marketPair == b:
                if setStat == a:
                    print("LowerPegValue is:")
                    print(lowerPegValue)
                    nonFiatVal = lowerPegValue / marketBTC
                    print("NonFiatVal is:")
                    print(nonFiatVal)
                    volume = nonFiatVal/peg
                    print("Volume for b is:")
                    print(volume)

                if setStat == s:
                    volume = setVolume

            if marketPair != b:
                volume = belowVal / peg

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
            print("Matrix Resolution is " + str(resolution + 1))

        else:
            print("This is the matrix peg price: " + str(line6[1]))
            print(line6)
            retrace_dict[str(line6[1]) + ' buy'] = matrix[(line6[0] + 1)][1]
            retrace_dict[str(line6[1]) + ' sell'] = matrix[(line6[0] - 1)][1]

    print(matrix)

    saveMatrix = input("Do you want to save the matrices to a local files? y or n")
    if saveMatrix == y:

        with open('/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/matrixGDAX-' + marketPair + '.pickle', 'wb')\
                as handle:
            pickle.dump(matrix, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open('/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/upperMatrixGDAX-' + marketPair + '.pickle', 'wb')\
                as handle:
            pickle.dump(upperMatrix, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open('/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/lowerMatrixGDAX-' + marketPair + '.pickle', 'wb')\
                as handle:
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
            "How do u want to divide your pillar buy above/below? .5 is 50/50, .2 is .2 above .8 below?")

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
        lNumberP = resolutionBelow
        mNumberP = resolutionBelowP + 1
        uNumberP = mNumberP
        pillarCount = 0

        print("Count is " + str(countP))

        print("Current Market Price: " + str(marketP))

        while pillarCount < countP:

            if countP > mNumberP:

                pegP = pillarMakerU + upperSpreadP

                volumeP = aboveVolP

                rPegP = round(pegP, marketDec)

                strPegP = str(rPegP)

                if marketPair != b:

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

            pillarCount = pillarCount + 1
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
            "/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/pillars_retraceDict-" + marketPair + ".txt", 'w'))

    y = 0
    Y = y
    n = 1
    N = n
    upperPegOrder = {}

    saveVars = input("Do you want to save the variables from the matrix? y or n?")

    if saveVars == y:

        json.dump(matrix_dict, open(
            "/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/GDAX_matrix_variable_save-" + marketPair + ".txt", 'w'))
        json.dump(retrace_dict, open(
            "/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/retraceDict-" + marketPair + ".txt", 'w'))
        json.dump(pillar_dict, open(
            "/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/pillarDict-" + marketPair + ".txt", 'w'))

    doWhat = input("Do you want to exit or set up a matrix? y or s?")

    if doWhat == y:
        exit()

if doWhat == s:

    a = 'LTC-USD'
    b = 'LTC-BTC'
    c = 'BTC-USD'

    A = a
    B = b
    C = c

    whichMatrix = input('Which of ur matrix files do u want to build from?'
                        'a. LTC-USD b. LTC-BTC c. BTC-USD')

    if whichMatrix == a:
        marketDec = 2
    if whichMatrix == b:
        marketDec = 5
    if whichMatrix == c:
        marketDec = 2

    matrixVs = json.load(
        open("/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/"
             "GDAX_matrix_variable_save-" + whichMatrix + ".txt"))

    print("Archived Market Price Saved Matrices were built on: " + str(matrixVs['Market Price']))

    marketPr = requests.get(api_url + '/products/' + whichMatrix + '/ticker')
    jsonPrice = marketPr.json()
    marketPr = float(jsonPrice['ask'])
    marketCurrent = round(marketPr, marketDec)

    print("Current Market Price: " + str(marketCurrent))

    print("Total Resolution: " + str(matrixVs['Total Resolution']))

    with open('/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/matrixGDAX-' + whichMatrix + '.pickle', 'rb')\
            as handle:
        matrixRead = pickle.load(handle)

    print("This is the matrix:")
    print(matrixRead)

    with open('/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/upperMatrixGDAX-' + whichMatrix + '.pickle', 'rb')\
            as handle:
        upperMatrixRead = pickle.load(handle)

    print("This is the upper matrix:")
    print(upperMatrixRead)

    with open('/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/lowerMatrixGDAX-' + whichMatrix + '.pickle', 'rb')\
            as handle:
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

    doWhat = input("Do you want to exit or run the re-buy engine? y or e?")

    if doWhat == y:
        exit()

if doWhat == e:

    a = 'LTC-USD'
    b = 'LTC-BTC'
    c = 'BTC-USD'

    A = a
    B = b
    C = c

    marketPair = input("Which market do you want to run Eden in? \n"
                        "a. LTC-USD b. LTC-BTC c. BTC-USD")

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

 u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'756.6462255000000000', u'order_id': u'2fb1217e-8488-4fde-8b00-ff6db123f349', u'created_at': u'2017-12-24T16:29:12.466Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01963000', u'trade_id': 2579411, u'settled': True, u'liquidity': u'M', u'size': u'2.75144082'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'0.2101518600000000', u'order_id': u'9fdc4dc8-e3a8-43ec-a7e4-d8b89f31bc9d', u'created_at': u'2017-12-24T15:50:50.467Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01963000', u'trade_id': 2578824, u'settled': True, u'liquidity': u'M', u'size': u'0.00077404'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'56.9405981400000000', u'order_id': u'9fdc4dc8-e3a8-43ec-a7e4-d8b89f31bc9d', u'created_at': u'2017-12-24T15:50:50.388Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01963000', u'trade_id': 2578823, u'settled': True, u'liquidity': u'M', u'size': u'0.20972596'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'64.4487850000000000', u'order_id': u'04856cf8-bf49-4a4d-8c7e-5288ce0bf7be', u'created_at': u'2017-12-23T22:31:20.2Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01929000', u'trade_id': 2551393, u'settled': True, u'liquidity': u'M', u'size': u'0.21050000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'66.2106700000000000', u'order_id': u'd8d6b3a1-96fb-4a15-8c75-4a9193f850ba', u'created_at': u'2017-12-23T14:54:34.463Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01963000', u'trade_id': 2536003, u'settled': True, u'liquidity': u'M', u'size': u'0.21050000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'11.9012000000000000', u'order_id': u'541f8098-4208-42f3-a849-15b1ca2f5751', u'created_at': u'2017-12-23T12:27:14.718Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01933000', u'trade_id': 2530074, u'settled': True, u'liquidity': u'M', u'size': u'0.04000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'10.4452000000000000', u'order_id': u'fd995135-a7f4-43f9-a951-8a9705c09d81', u'created_at': u'2017-12-23T06:23:14.836Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01899000', u'trade_id': 2524352, u'settled': True, u'liquidity': u'M', u'size': u'0.04000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'11.2996000000000000', u'order_id': u'0eaed9f8-aa00-4bff-a388-9bf11b0f760d', u'created_at': u'2017-12-23T03:23:34.624Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01933000', u'trade_id': 2521192, u'settled': True, u'liquidity': u'M', u'size': u'0.04000000'}, {u'fee': u'0.0000045912000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'22.1600000000000000', u'order_id': u'efd61bf8-6733-4fef-a7ea-28c9a5a12bfc', u'created_at': u'2017-12-23T03:08:09.723Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01913000', u'trade_id': 2520527, u'settled': True, u'liquidity': u'T', u'size': u'0.08000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'10.1600000000000000', u'order_id': u'1c3a5869-7dcc-4885-be2b-6a8c01ba3909', u'created_at': u'2017-12-22T23:46:04.686Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01833000', u'trade_id': 2515094, u'settled': True, u'liquidity': u'M', u'size': u'0.04000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'10.4484000000000000', u'order_id': u'57634ec2-79f7-4f54-8279-93cc7b7bcea4', u'created_at': u'2017-12-22T23:40:07.81Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01866000', u'trade_id': 2514445, u'settled': True, u'liquidity': u'M', u'size': u'0.04000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'11.6640000000000000', u'order_id': u'c4251e12-3342-46da-ac5c-1e9de4aac42e', u'created_at': u'2017-12-22T22:52:00.785Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01899000', u'trade_id': 2511511, u'settled': True, u'liquidity': u'M', u'size': u'0.04000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'11.5096000000000000', u'order_id': u'8dea033b-c419-475f-9aee-abd6a1f7d7b0', u'created_at': u'2017-12-22T22:36:04.42Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01920000', u'trade_id': 2510102, u'settled': True, u'liquidity': u'M', u'size': u'0.04000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'11.3548000000000000', u'order_id': u'52e6bed0-15bd-49de-8389-beed2f3ab14e', u'created_at': u'2017-12-22T21:27:37.773Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01966000', u'trade_id': 2505686, u'settled': True, u'liquidity': u'M', u'size': u'0.04000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'11.2868000000000000', u'order_id': u'30945c00-f108-450e-985d-32c71421c26d', u'created_at': u'2017-12-22T20:46:31.151Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01933000', u'trade_id': 2501981, u'settled': True, u'liquidity': u'M', u'size': u'0.04000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'10.3808000000000000', u'order_id': u'db4f8fcf-e9d4-4ae1-a238-8bb338282a05', u'created_at': u'2017-12-22T19:06:27.192Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01899000', u'trade_id': 2495466, u'settled': True, u'liquidity': u'M', u'size': u'0.04000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'9.6000000000000000', u'order_id': u'299cb28e-44e9-4915-a9d4-45ec906331b1', u'created_at': u'2017-12-22T18:18:13.895Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01866000', u'trade_id': 2491754, u'settled': True, u'liquidity': u'M', u'size': u'0.04000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'8.8860000000000000', u'order_id': u'4831d00c-1ea3-4f58-a706-00b1e61cfad0', u'created_at': u'2017-12-22T16:26:50.34Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01766000', u'trade_id': 2486457, u'settled': True, u'liquidity': u'M', u'size': u'0.04000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'9.3048000000000000', u'order_id': u'3bb94ed4-2ecf-489d-9f72-ce7f78002397', u'created_at': u'2017-12-22T16:03:16.08Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01799000', u'trade_id': 2484454, u'settled': True, u'liquidity': u'M', u'size': u'0.04000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'10.3604000000000000', u'order_id': u'd140e960-de0f-442e-8d51-895d888938be', u'created_at': u'2017-12-22T15:51:32.495Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01899000', u'trade_id': 2483190, u'settled': True, u'liquidity': u'M', u'size': u'0.04000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'9.9592000000000000', u'order_id': u'9f66eb2d-cd93-4835-a974-0bbd3ae06f11', u'created_at': u'2017-12-22T15:43:09.846Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01833000', u'trade_id': 2482076, u'settled': True, u'liquidity': u'M', u'size': u'0.04000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'2.3928702372000000', u'order_id': u'7032ee79-45e1-4d5b-b11f-4bdcc0e8ee73', u'created_at': u'2017-12-22T15:42:14.187Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01866000', u'trade_id': 2481971, u'settled': True, u'liquidity': u'M', u'size': u'0.00944082'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'7.7455297628000000', u'order_id': u'7032ee79-45e1-4d5b-b11f-4bdcc0e8ee73', u'created_at': u'2017-12-22T15:42:13.958Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01866000', u'trade_id': 2481970, u'settled': True, u'liquidity': u'M', u'size': u'0.03055918'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'10.2356000000000000', u'order_id': u'753ec572-13ad-48af-8cd1-316ce4a221b1', u'created_at': u'2017-12-22T15:41:46.143Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01866000', u'trade_id': 2481790, u'settled': True, u'liquidity': u'M', u'size': u'0.04000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'9.9144000000000000', u'order_id': u'83f37acb-2387-4486-8bbe-a30977509ae8', u'created_at': u'2017-12-22T15:40:59.168Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01850000', u'trade_id': 2481615, u'settled': True, u'liquidity': u'M', u'size': u'0.04000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'9.7012000000000000', u'order_id': u'1d455ce1-fa29-439b-be96-f1e28c04c588', u'created_at': u'2017-12-22T15:39:42.818Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01833000', u'trade_id': 2481251, u'settled': True, u'liquidity': u'M', u'size': u'0.04000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'8.8820000000000000', u'order_id': u'dedd82d3-2cf4-4ea7-94fb-c8c762c44b8f', u'created_at': u'2017-12-22T15:18:28.306Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01766000', u'trade_id': 2477678, u'settled': True, u'liquidity': u'M', u'size': u'0.04000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'9.2800000000000000', u'order_id': u'd79c52d2-a4fb-4002-aa45-c15718e3a198', u'created_at': u'2017-12-22T15:17:24.658Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01799000', u'trade_id': 2477256, u'settled': True, u'liquidity': u'M', u'size': u'0.04000000'}, {u'fee': u'0.0000467910000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'199.8270000000000000', u'order_id': u'4bc4ac85-af34-4fa3-8d5a-fe9107344ccd', u'created_at': u'2017-12-22T15:15:46.173Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01733000', u'trade_id': 2476589, u'settled': True, u'liquidity': u'T', u'size': u'0.90000000'}, {u'fee': u'0.0000051990000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'22.2030000000000000', u'order_id': u'4bc4ac85-af34-4fa3-8d5a-fe9107344ccd', u'created_at': u'2017-12-22T15:15:46.173Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01733000', u'trade_id': 2476588, u'settled': True, u'liquidity': u'T', u'size': u'0.10000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'189.7900000000000000', u'order_id': u'077036b0-2384-49c8-a4f9-7fecd1a251ac', u'created_at': u'2017-12-22T14:35:28.781Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01638000', u'trade_id': 2472798, u'settled': True, u'liquidity': u'M', u'size': u'1.00000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'6.2736000000000000', u'order_id': u'0dc13bcb-e9f3-4a3d-89be-3ef3b3958499', u'created_at': u'2017-12-22T14:20:04.718Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01499000', u'trade_id': 2469740, u'settled': True, u'liquidity': u'M', u'size': u'0.04000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'6.7676000000000000', u'order_id': u'd9d7acbd-9225-4956-913b-199161347406', u'created_at': u'2017-12-22T14:18:33.911Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01533000', u'trade_id': 2469137, u'settled': True, u'liquidity': u'M', u'size': u'0.04000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'6.9196000000000000', u'order_id': u'922019f4-320c-4977-806b-7a0f2a698f3e', u'created_at': u'2017-12-22T14:15:19.296Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01566000', u'trade_id': 2467877, u'settled': True, u'liquidity': u'M', u'size': u'0.04000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'7.0000000000000000', u'order_id': u'379f79da-5ef8-4d59-b0ea-127431bd2e22', u'created_at': u'2017-12-22T14:14:42.53Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01599000', u'trade_id': 2467570, u'settled': True, u'liquidity': u'M', u'size': u'0.04000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'7.3996000000000000', u'order_id': u'01413092-0721-4f87-be27-08393501f5c8', u'created_at': u'2017-12-22T14:11:20.714Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01633000', u'trade_id': 2466926, u'settled': True, u'liquidity': u'M', u'size': u'0.04000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'7.6000000000000000', u'order_id': u'8636f33c-4427-4ffc-826f-9605f1f58058', u'created_at': u'2017-12-22T14:07:10.383Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01665000', u'trade_id': 2466185, u'settled': True, u'liquidity': u'M', u'size': u'0.04000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'7.8236000000000000', u'order_id': u'e1bc30e9-d489-47bd-be8d-5b856a7d56b2', u'created_at': u'2017-12-22T14:06:02.153Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01699000', u'trade_id': 2465903, u'settled': True, u'liquidity': u'M', u'size': u'0.04000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'8.6276000000000000', u'order_id': u'a31a3149-77a5-4494-9b8f-9b67536eff6d', u'created_at': u'2017-12-22T13:29:47.337Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01733000', u'trade_id': 2463161, u'settled': True, u'liquidity': u'M', u'size': u'0.04000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'9.1200000000000000', u'order_id': u'4f18eaa9-7b47-47ad-af01-995bc3095372', u'created_at': u'2017-12-22T13:14:41.75Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01766000', u'trade_id': 2462076, u'settled': True, u'liquidity': u'M', u'size': u'0.04000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'9.9068000000000000', u'order_id': u'4275401f-e369-4879-af1e-377b26e07ac2', u'created_at': u'2017-12-22T11:41:38.581Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01799000', u'trade_id': 2459785, u'settled': True, u'liquidity': u'M', u'size': u'0.04000000'}, {u'fee': u'0.0000044040000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'20.5160000000000000', u'order_id': u'ea73adf1-0014-4503-a575-f73a9c871513', u'created_at': u'2017-12-22T11:03:00.8Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01835000', u'trade_id': 2458644, u'settled': True, u'liquidity': u'T', u'size': u'0.08000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'9.1188000000000000', u'order_id': u'640dcbca-3d0a-4bec-9643-e26b73b2fefd', u'created_at': u'2017-12-22T07:19:38.203Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01766000', u'trade_id': 2446469, u'settled': True, u'liquidity': u'M', u'size': u'0.04000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'9.6184000000000000', u'order_id': u'73e147d8-3ab6-4b44-ba83-df563c798e02', u'created_at': u'2017-12-22T07:13:53.858Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01799000', u'trade_id': 2445942, u'settled': True, u'liquidity': u'M', u'size': u'0.04000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'9.9340000000000000', u'order_id': u'e48acdde-a07c-4972-9440-84211a7ecdc7', u'created_at': u'2017-12-22T07:10:39.154Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01833000', u'trade_id': 2445496, u'settled': True, u'liquidity': u'M', u'size': u'0.04000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'9.3004000000000000', u'order_id': u'2481a2bf-4051-4801-9b85-21ec633f228c', u'created_at': u'2017-12-22T03:19:51.458Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01866000', u'trade_id': 2431557, u'settled': True, u'liquidity': u'M', u'size': u'0.04000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'10.5956000000000000', u'order_id': u'605d95d0-61b3-46bd-b38d-804247bf9ab4', u'created_at': u'2017-12-22T02:53:44.875Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01899000', u'trade_id': 2427969, u'settled': True, u'liquidity': u'M', u'size': u'0.04000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'11.5200000000000000', u'order_id': u'c52f831e-6aae-43ab-99ae-87a1137815b8', u'created_at': u'2017-12-22T02:17:33.724Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01933000', u'trade_id': 2425848, u'settled': True, u'liquidity': u'M', u'size': u'0.04000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'204.1136000000000000', u'order_id': u'93b61414-84fb-4575-a836-adef52e98269', u'created_at': u'2017-12-20T00:21:49.356Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01924000', u'trade_id': 2340755, u'settled': True, u'liquidity': u'M', u'size': u'0.61480000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'223.3199520000000000', u'order_id': u'021f484c-e414-48c8-a92c-a32f784c875d', u'created_at': u'2017-12-19T18:59:32.174Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01974000', u'trade_id': 2326330, u'settled': True, u'liquidity': u'M', u'size': u'0.61480000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'240.7510000000000000', u'order_id': u'e0125400-0560-44a8-ad1a-9dfbb6bdc766', u'created_at': u'2017-12-19T12:09:09.137Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01924000', u'trade_id': 2313961, u'settled': True, u'liquidity': u'M', u'size': u'0.70000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'213.1819000000000000', u'order_id': u'9446ff26-1dd6-45ea-a165-1fb5a3b2a28e', u'created_at': u'2017-12-19T10:12:51.531Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01874000', u'trade_id': 2310629, u'settled': True, u'liquidity': u'M', u'size': u'0.61480000'}, {u'fee': u'0.0000149551197300', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'94.1014139460000000', u'order_id': u'a524eb2d-7765-4e8d-a8f5-d933ef1492e1', u'created_at': u'2017-12-19T08:26:35.255Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01915000', u'trade_id': 2308078, u'settled': True, u'liquidity': u'T', u'size': u'0.26031540'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'250.7454918657000000', u'order_id': u'6ea666bf-172f-454b-93a0-78cb7564bf84', u'created_at': u'2017-12-19T07:35:17.866Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01924000', u'trade_id': 2306823, u'settled': True, u'liquidity': u'M', u'size': u'0.68823729'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'58.3430735380000000', u'order_id': u'43638a0e-c115-49e8-a442-88872d7d0b18', u'created_at': u'2017-12-19T04:31:39.507Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01990000', u'trade_id': 2300324, u'settled': True, u'liquidity': u'M', u'size': u'0.15398420'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'187.3450000000000000', u'order_id': u'84c1c0d8-2e96-498c-98a3-b0903ab3764b', u'created_at': u'2017-12-19T04:09:38.962Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01974000', u'trade_id': 2298963, u'settled': True, u'liquidity': u'M', u'size': u'0.50000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'226.1357360000000000', u'order_id': u'656d0a52-0a91-4993-8eb9-d45241f45ad0', u'created_at': u'2017-12-19T03:57:27.524Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01924000', u'trade_id': 2297858, u'settled': True, u'liquidity': u'M', u'size': u'0.61480000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'218.9801051360000000', u'order_id': u'8cd138e1-6399-4f61-8ea7-d3a3d552fe48', u'created_at': u'2017-12-18T23:54:58.722Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01874000', u'trade_id': 2288492, u'settled': True, u'liquidity': u'M', u'size': u'0.61476728'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'181.2650000000000000', u'order_id': u'ea4280e5-7306-45bd-9546-c88392f1ad4d', u'created_at': u'2017-12-18T22:56:17.109Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01924000', u'trade_id': 2283732, u'settled': True, u'liquidity': u'M', u'size': u'0.50000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'175.9700000000000000', u'order_id': u'9fb82828-b6c1-4d5f-8b6f-f66c8cf50969', u'created_at': u'2017-12-18T22:25:49.313Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01874000', u'trade_id': 2279058, u'settled': True, u'liquidity': u'M', u'size': u'0.50000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'35.1940000000000000', u'order_id': u'f482bf17-f288-49b8-8bb6-33ec429f3267', u'created_at': u'2017-12-18T22:25:49.313Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01874000', u'trade_id': 2279057, u'settled': True, u'liquidity': u'M', u'size': u'0.10000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'169.5950000000000000', u'order_id': u'95572723-3fa1-47ad-87a1-43b50822414d', u'created_at': u'2017-12-18T20:30:25.717Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01824000', u'trade_id': 2272173, u'settled': True, u'liquidity': u'M', u'size': u'0.50000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'67.8380000000000000', u'order_id': u'af31b36a-39be-4fb6-85cc-59fc307937ea', u'created_at': u'2017-12-18T20:30:25.717Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01824000', u'trade_id': 2272170, u'settled': True, u'liquidity': u'M', u'size': u'0.20000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'164.9300000000000000', u'order_id': u'35097418-ab15-432c-b3fa-c134db8db874', u'created_at': u'2017-12-18T20:27:10.64Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01774000', u'trade_id': 2271545, u'settled': True, u'liquidity': u'M', u'size': u'0.50000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'65.9720000000000000', u'order_id': u'd15bc0f8-8527-4431-ab1f-e87818b91db3', u'created_at': u'2017-12-18T20:27:10.64Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01774000', u'trade_id': 2271544, u'settled': True, u'liquidity': u'M', u'size': u'0.20000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'160.7100000000000000', u'order_id': u'a4e357d1-86c3-41d4-be8c-9830362f084f', u'created_at': u'2017-12-18T17:11:29.526Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01724000', u'trade_id': 2265495, u'settled': True, u'liquidity': u'M', u'size': u'0.50000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'64.2840000000000000', u'order_id': u'3e919232-8bb7-4e72-a641-e1e8092e20a2', u'created_at': u'2017-12-18T17:11:29.526Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01724000', u'trade_id': 2265494, u'settled': True, u'liquidity': u'M', u'size': u'0.20000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'227.8780000000000000', u'order_id': u'8791ac6c-acc0-47f8-b127-5335ffd12e4b', u'created_at': u'2017-12-17T18:41:41.932Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01674000', u'trade_id': 2233620, u'settled': True, u'liquidity': u'M', u'size': u'0.70000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'227.0800000000000000', u'order_id': u'407bdc6b-02be-4183-abb8-82afac7b62cd', u'created_at': u'2017-12-17T12:14:53.624Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01624000', u'trade_id': 2224794, u'settled': True, u'liquidity': u'M', u'size': u'0.70000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'229.0890000000000000', u'order_id': u'5bf993d9-d086-41c4-98a0-ac6408a227dd', u'created_at': u'2017-12-17T05:57:49.306Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01674000', u'trade_id': 2215061, u'settled': True, u'liquidity': u'M', u'size': u'0.70000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'159.6300000000000000', u'order_id': u'49274f17-9d4e-4719-bb8e-f478c355969d', u'created_at': u'2017-12-17T02:20:22.049Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01624000', u'trade_id': 2207288, u'settled': True, u'liquidity': u'M', u'size': u'0.50000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'63.8520000000000000', u'order_id': u'6ac89258-5a17-4a51-9260-0a6dbce33db4', u'created_at': u'2017-12-17T02:20:22.049Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01624000', u'trade_id': 2207287, u'settled': True, u'liquidity': u'M', u'size': u'0.20000000'}, {u'fee': u'0.0000478332541632', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'304.9083868848000000', u'order_id': u'f0937425-f78e-4259-812b-76d43db26fdf', u'created_at': u'2017-12-17T02:06:00.545Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01672000', u'trade_id': 2206486, u'settled': True, u'liquidity': u'T', u'size': u'0.95361352'}, {u'fee': u'0.0000023281374312', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'14.8316131152000000', u'order_id': u'f0937425-f78e-4259-812b-76d43db26fdf', u'created_at': u'2017-12-17T02:06:00.545Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01673000', u'trade_id': 2206485, u'settled': True, u'liquidity': u'T', u'size': u'0.04638648'}, {u'fee': u'0.0001005000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'639.2800000000000000', u'order_id': u'9a64384e-158a-454c-b0a7-20579696a947', u'created_at': u'2017-12-17T02:05:46.475Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01675000', u'trade_id': 2206482, u'settled': True, u'liquidity': u'T', u'size': u'2.00000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'645.2800000000000000', u'order_id': u'7fb73d47-4bdc-4e74-9119-a21408276475', u'created_at': u'2017-12-17T02:02:49.373Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01684000', u'trade_id': 2206343, u'settled': True, u'liquidity': u'M', u'size': u'2.00000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'161.4400000000000000', u'order_id': u'c316fa0d-03e6-43e1-be52-1aad61164cff', u'created_at': u'2017-12-17T02:00:51.07Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01674000', u'trade_id': 2206134, u'settled': True, u'liquidity': u'M', u'size': u'0.50000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'65.1940000000000000', u'order_id': u'312e58c1-bda8-4237-94ff-ce55b02fe868', u'created_at': u'2017-12-17T01:46:02.807Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01674000', u'trade_id': 2204258, u'settled': True, u'liquidity': u'M', u'size': u'0.20000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'65.7860000000000000', u'order_id': u'14d4b4de-b099-41e2-a53f-0070aff604d7', u'created_at': u'2017-12-17T01:41:04.619Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01724000', u'trade_id': 2202891, u'settled': True, u'liquidity': u'M', u'size': u'0.20000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'63.5320000000000000', u'order_id': u'e877384f-0274-4fbc-94d2-dcfa9731e0db', u'created_at': u'2017-12-17T01:27:36.86Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01674000', u'trade_id': 2200081, u'settled': True, u'liquidity': u'M', u'size': u'0.20000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'62.3720000000000000', u'order_id': u'e74b9446-dd26-40a2-8413-7923b3ca44d6', u'created_at': u'2017-12-17T01:14:02.572Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01624000', u'trade_id': 2198508, u'settled': True, u'liquidity': u'M', u'size': u'0.20000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'61.3980000000000000', u'order_id': u'e43ac853-d2ca-4f0c-9546-e480770ec65f', u'created_at': u'2017-12-17T00:00:46.919Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01574000', u'trade_id': 2194373, u'settled': True, u'liquidity': u'M', u'size': u'0.20000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'59.1340000000000000', u'order_id': u'06b0681d-ffaa-47e1-ae2d-a1ebdef7d6cd', u'created_at': u'2017-12-16T19:21:18.429Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01524000', u'trade_id': 2181627, u'settled': True, u'liquidity': u'M', u'size': u'0.20000000'}, {u'fee': u'0.0000095760000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'60.2940000000000000', u'order_id': u'a55a4303-9a6e-42bd-9fcd-c486925fd146', u'created_at': u'2017-12-16T17:23:38.308Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01596000', u'trade_id': 2178464, u'settled': True, u'liquidity': u'T', u'size': u'0.20000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'59.0200000000000000', u'order_id': u'3638ac26-c19a-41a8-a5e1-a1d830b6d853', u'created_at': u'2017-12-16T16:01:57.734Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01524000', u'trade_id': 2174056, u'settled': True, u'liquidity': u'M', u'size': u'0.20000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'60.2400000000000000', u'order_id': u'e82cf906-ff76-4cae-9b46-376b45f6bc63', u'created_at': u'2017-12-16T15:45:46.082Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01574000', u'trade_id': 2172301, u'settled': True, u'liquidity': u'M', u'size': u'0.20000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'61.2180000000000000', u'order_id': u'684d6061-a810-4da2-86b3-214c91c01f2a', u'created_at': u'2017-12-16T13:36:57.756Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01623000', u'trade_id': 2165718, u'settled': True, u'liquidity': u'M', u'size': u'0.20000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'31.0010000000000000', u'order_id': u'2765d58c-6202-4ed2-b632-de164da9511b', u'created_at': u'2017-12-16T13:25:05.894Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01649000', u'trade_id': 2164654, u'settled': True, u'liquidity': u'M', u'size': u'0.10000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'60.9820000000000000', u'order_id': u'5878b0ec-0230-4acc-9610-eb45d4a75d30', u'created_at': u'2017-12-16T11:15:45.387Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01673000', u'trade_id': 2161028, u'settled': True, u'liquidity': u'M', u'size': u'0.20000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'60.0000000000000000', u'order_id': u'ee8c189b-4e0a-4619-b1d3-6f5520e1d719', u'created_at': u'2017-12-16T07:23:59.745Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01624000', u'trade_id': 2155326, u'settled': True, u'liquidity': u'M', u'size': u'0.20000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'60.5660000000000000', u'order_id': u'cf8aaecf-7590-4ce1-b132-1017d14a0d76', u'created_at': u'2017-12-16T06:46:35.839Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01674000', u'trade_id': 2153966, u'settled': True, u'liquidity': u'M', u'size': u'0.20000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'61.4100000000000000', u'order_id': u'836efce5-d5c9-4d1d-b118-049332894c69', u'created_at': u'2017-12-16T01:15:23.884Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01724000', u'trade_id': 2145983, u'settled': True, u'liquidity': u'M', u'size': u'0.20000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'60.4180000000000000', u'order_id': u'7428214d-5ed7-494c-ae3c-bc43f8b4cc40', u'created_at': u'2017-12-16T00:24:46.924Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01674000', u'trade_id': 2144249, u'settled': True, u'liquidity': u'M', u'size': u'0.20000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'61.7400000000000000', u'order_id': u'fedb30b2-48fe-45ba-80e7-2346df74558a', u'created_at': u'2017-12-15T20:39:00.53Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01724000', u'trade_id': 2137326, u'settled': True, u'liquidity': u'M', u'size': u'0.20000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'62.5860000000000000', u'order_id': u'0bb17820-26a4-4783-b76d-a20122bfe4d4', u'created_at': u'2017-12-15T19:59:10.806Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01774000', u'trade_id': 2135528, u'settled': True, u'liquidity': u'M', u'size': u'0.20000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'60.9100000000000000', u'order_id': u'bde7e1c2-a9cf-4e92-87f5-cf629f400f92', u'created_at': u'2017-12-15T19:19:35.449Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'sell', u'price': u'0.01724000', u'trade_id': 2134154, u'settled': True, u'liquidity': u'M', u'size': u'0.20000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'60.6000000000000000', u'order_id': u'2aec4b96-ad58-46be-a40a-680420469dfc', u'created_at': u'2017-12-15T18:58:39.185Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01674000', u'trade_id': 2132743, u'settled': True, u'liquidity': u'M', u'size': u'0.20000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'60.8000000000000000', u'order_id': u'76cc25a8-315d-4787-9404-f3e1f30a6b43', u'created_at': u'2017-12-15T18:22:09.105Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01724000', u'trade_id': 2130273, u'settled': True, u'liquidity': u'M', u'size': u'0.20000000'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'33.7145615920000000', u'order_id': u'91fd03d3-118c-4fcc-8f2a-2c3ac6b28564', u'created_at': u'2017-12-15T17:36:14.014Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01769000', u'trade_id': 2127427, u'settled': True, u'liquidity': u'M', u'size': u'0.10723120'}, {u'fee': u'0.0000000000000000', u'user_id': u'551ed203be25592e4c000034', u'product_id': u'LTC-BTC', u'usd_volume': u'62.8000000000000000', u'order_id': u'262499fc-6b78-4911-a7d6-8b1b78f00427', u'created_at': u'2017-12-15T17:26:37.917Z', u'profile_id': u'd0486eba-a6ef-47cb-9175-25cf9a304959', u'side': u'buy', u'price': u'0.01774000', u'trade_id': 2126926, u'settled': True, u'liquidity': u'M', u'size': u'0.20000000'}]
Traceback (most recent call last):
  File "/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/J-GDAX-d3a-Add-Coin-to-Coin.py", line 1041, in <module>
    marketPr = requests.get(api_url + '/products/' + marketPair + '/ticker')
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

Traceback (most recent call last):
  File "/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/J-GDAX-d3a-Add-Coin-to-Coin.py", line 1041, in <module>
    marketPr = requests.get(api_url + '/products/' + marketPair + '/ticker')
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


Traceback (most recent call last):
  File "./J-GDAX-d3a-Add-Coin-to-Coin.py", line 1020, in <module>
    api_url + '/fills?cb-before=' + str(last_fill_dealt_withE) + '&product_id=' + marketPair, auth=auth)
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
requests.exceptions.ConnectionError: HTTPSConnectionPool(host='api.gdax.com', port=443): Max retries exceeded with url: /fills?cb-before=194d51c6-28be-4cbd-9010-8cfee22ed6a3&product_id=LTC-BTC (Caused by NewConnectionError('<urllib3.connection.VerifiedHTTPSConnection object at 0x1088e8390>: Failed to establish a new connection: [Errno 8] nodename nor servname provided, or not known',))

'''