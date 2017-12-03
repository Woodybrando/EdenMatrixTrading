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
retrace_dict = {}
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

    if marketPair == a:
        marketDec = 2
        matrix_dict['marketDec'] = marketDec
    elif marketPair == b:
        marketDec = 6
        matrix_dict['marketDec'] = marketDec
    elif marketPair == c:
        marketDec = 2
        matrix_dict['marketDec'] = marketDec


    # Add a way to set what entry point u want to start your matrix say if market is 75.5
    # and u want to start only if price = 73

    matrix_dict['Market Pair'] = marketPair

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


    matrix_dict['Market Price'] = marketP

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

    lowerBuy = initInv - upperBuy

    matrix_dict['Below Buy'] = lowerBuy

    print("Upper Cost minus Fee " + str(upperBuy))

    aboveCoins = aboveInv/marketP

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

    aboveVol = round(aboveCoins/(resolutionAbove), 4)

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

    unroundVal = belowBuys/(resolutionBelow)

    matrix_dict['Unrounded Below Peg Value'] = unroundVal

    belowVal = round(unroundVal, 4)

    matrix_dict['Below Peg Value'] = belowVal

    print("Below Value Per Peg: " + str(belowVal))

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


    upperSpread = (marketTop - marketP) / (resolutionAbove)
    lowerSpread = (marketP - marketBottom) / (resolutionBelow)

    matrix_dict['Upper Spread'] = upperSpread
    matrix_dict['Lower Spread'] = lowerSpread

    print("Upper Spread " + str(upperSpread))
    print("Lower Spread " + str(lowerSpread))

    marketUpper = marketP + (upperSpread / 2)
    marketLower = marketP - (lowerSpread / 2)

    matrix_dict['Market Upper'] = marketUpper
    matrix_dict['Market Lower'] = marketLower

    print("MarketUpper is " + str(marketUpper))
    print("MarketLower is " + str(marketLower))


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



    lNumber = resolutionBelow - 2
    mNumber = resolutionBelow - 1
    uNumber = resolutionBelow

    #lNumber = 23
    #mNumber = 24
    #uNumber = 25

    print("Count is " + str(count))

    print("Current Market Price: " + str(marketPr))

    while count > -1:

        peg = pegMakerU + upperSpread

        #print("Count is " + str(count))
        #print("Peg is " + str(peg))

        if count > mNumber:

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

        elif count == mNumber:
            peg = marketP
            rPeg = round(peg, 2)
            volume = aboveVol
            number = mNumber
            list = number, rPeg, round(volume, 4)
            matrix.append(list)

        elif count < mNumber:
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

    for line6 in matrix:
        if line6[0] == 0:
            print("This is the matrix peg price: " + str(line6[1]))
            retrace_dict[str(line6[1]) + ' buy'] = matrix[(line6[0] + 1)]
            print("Market hit your matrix bottom")

        elif line6[0] == resolution:
            print("This is the matrix peg price: " + str(line6[1]))
            retrace_dict[str(line6[1]) + ' sell'] = matrix[(line6[0] - 1)][1]
            print("Market hit your matrix top")

        else:
            print("This is the matrix peg price: " + str(line6[1]))
            retrace_dict[str(line6[1]) + ' buy'] = matrix[(line6[0] + 1)][1]
            retrace_dict[str(line6[1]) + ' sell'] = matrix[(line6[0] - 1)][1]

        #matrix_dict['Total Resolution'] = resolution

    print(matrix)

    saveMatrix = input("Do you want to save the matrices to a local files? y or n")
    if saveMatrix == y:

        with open('/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/matrixGDAX.pickle', 'wb') as handle:
            pickle.dump(matrix, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open('/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/upperMatrixGDAX.pickle', 'wb') as handle:
            pickle.dump(upperMatrix, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open('/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/lowerMatrixGDAX.pickle', 'wb') as handle:
            pickle.dump(lowerMatrix, handle, protocol=pickle.HIGHEST_PROTOCOL)

    '''
        with open("/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/matrixGDAX.py", 'w') as graphd:
            for row in matrix:
                print >> graphd, ', '.join(map(str, row))

        with open("/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/upperMatrixGDAX.txt", 'w') as graphu:
            for row in upperMatrix:
                print >> graphu, ', '.join(map(str, row))

        with open("/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/lowerMatrixGDAX.txt", 'w') as graphl:
            for row in lowerMatrix:
                print >> graphl, ', '.join(map(str, row))
    '''

            #matrixFileHandle = json.load(matrix)
        #matrixFileHandle.close()

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

    print("Peg Values:")
    print(sumLower)

    print("Lower buys total cost " + str(lowerValAdd))

    totalMatrixCost = upperCost + lowerValAdd

    print("Total Matrix Cost " + str(totalMatrixCost))



    #print("Total Coin Cost: " + str(upperCost + lowerCost))

    y = 0
    Y = y
    n = 1
    N = n
    upperPegOrder = {}

    saveVars = input("Do you want to save the variables from the matrix? y or n?")

    if saveVars == y:

        json.dump(matrix_dict, open("/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/GDAX_matrix_variable_save.txt", 'w'))
        json.dump(retrace_dict, open("/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/retraceDict.txt", 'w'))

    exitAns = input("Do you want to exit? y or n?")

    if exitAns == y:
        exit()

    #for line in matrix:

elif doWhat == s:

    matrixVs = json.load(open("/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/GDAX_matrix_variable_save.txt"))



    print("Archived Market Price Saved Matrices were built on: " + str(matrixVs['Market Price']))

    marketPr = requests.get(api_url + '/products/LTC-USD/ticker')
    jsonPrice = marketPr.json()
    #print(jsonPrice['ask'])
    marketPr = float(jsonPrice['ask'])
    marketCurrent = round(marketPr, 2)


    print("Current Market Price: " + str(marketCurrent))

    print("Total Resolution: " + str(matrixVs['Total Resolution']))

    #matrixRead = []
    #upperMatrixRead = []
    #lowerMatrixRead = []

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

    '''
    with open('/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/matrixGDAX.py') as f:

        matrixLines = f.read().splitlines()
        for line4 in matrixLines:
            tupleNew = line4.split(',')

            matrixRead.append(tupleNew)

    print("This is the matrix:")
    print(matrixRead)

    with open('/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/upperMatrixGDAX.txt') as f:

        upperMatrixLines = f.read().splitlines()
        for line4 in upperMatrixLines:
            tupleNew = line4.split(',')

            upperMatrixRead.append(tupleNew)

    print("This is the upper matrix:")
    print(upperMatrixRead)


    with open('/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/lowerMatrixGDAX.txt') as f:

        lowerMatrixLines = f.read().splitlines()
        for line4 in lowerMatrixLines:
            tupleNew = line4.split(',')

            lowerMatrixRead.append(tupleNew)



    print("This is the lower matrix:")
    print(lowerMatrixRead)

    '''

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

    #activateEngine = input("Activate the rebuying engine!? y or n?")
    #if activateEngine == y:


elif doWhat == e:


    matrixVs = json.load(open("/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/GDAX_matrix_variable_save.txt"))

    print("Market Pair is: " + str(matrixVs['Market Pair']))

    Product_id = matrixVs['Market Pair']
    marketPast = matrixVs['Market Price']
    marketDec = matrixVs['marketDec']


    isTrue = 1

    with open('/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/matrixGDAX.pickle', 'rb') as handle:
        matrixRead = pickle.load(handle)

    print("This is the matrix:")
    print(matrixRead)
    # matrixFromFile.close()

    newSide = 'none'
    newPrice = '0'
    lastFill = 0

    while isTrue == 1:

        print("This is a fresh start through the Prime Loop")

        from pprint import pprint

        with open('/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/retraceDict.txt', 'r') as f:
            matrixDict = eval(f.read())


        last_fill_file_handleE = open(
            '/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/last_order_id_processed.txt', 'r+')
        last_fill_dealt_withE = last_fill_file_handleE.readline()
        print('this is the last order_id dealt with ' + last_fill_dealt_withE)
        last_fill_file_handleE.close()


        count2 = 0


        while count2 < 1000:

            print("This is a loop through the while count2 < 1000 while loop")


            requestFills = requests.get(
                api_url + '/fills?cb-before=' + str(last_fill_dealt_withE) + '&product_id=LTC-USD', auth=auth)

            # print(requestFills.json())
            jump = requestFills.json()

            outro = False



            if jump[0]['order_id'] == str(last_fill_dealt_withE):

                print("This prints when we have an order ID match")



                marketPr = requests.get(api_url + '/products/LTC-USD/ticker')
                jsonPrice = marketPr.json()
                #print(jsonPrice['ask'])
                marketPr = float(jsonPrice['ask'])
                marketP = round(marketPr, marketDec)


                #oneFillDict =

                # requests.post(api_url + '/orders', json=order, auth=auth)

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

                count2 = 1001

                time.sleep(5)


            elif count2 < 1000:

                print("This prints because we didn't have an order id match")

                jumpCount = 0



                #while jump[jumpCount]['order_id'] != str(last_fill_dealt_withE):

                for fill in jump:

                    print("This is number " + str(jumpCount) + " through the jump loop")

                    print("This is the jump order id:")
                    print(fill['order_id'])

                    print("This is the old order_id:")
                    print(str(last_fill_dealt_withE))

                    if count2 == 0:
                        last_order_dealt_withN = fill['order_id']
                        print("lastFill just got set to:")
                        print(fill['order_id'])

                    #fill = jump[jumpCount]

                    jumpCount = jumpCount + 1

                    if str(fill['order_id']) == str(last_fill_dealt_withE):

                        last_order_file_handle3 = open(
                        '/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/last_order_id_processed.txt',
                        'w')
                        last_order_file_handle3.write(str(lastFill))
                        count = 1001

                        print("Fill Order_Id is a match to the last_fill_dealt_withE")

                        print(str(fill['order_id']))

                        print("This is the final match and the str(last_fill_dealt_withE)")

                        print(str(last_fill_dealt_withE))

                        outro = True

                        print("Break in Match")

                        break

                    elif str(fill['order_id']) != str(last_fill_dealt_withE):

                        if outro is True:
                            print("Break in Non-Match")
                            break

                        print("Non-matching fill order_id is:")
                        print[str(fill['order_id'])]
                        print("Non-Matching str(last_fill_dealt_withE) is:")
                        print[str(last_fill_dealt_withE)]

                        #figure out how to print the fill index here

                        print("this is the fill:")
                        pprint(fill)
                        print("this is the fill price:")
                        pprint(fill['price'])
                        print("This is the fill side:")
                        pprint(fill['side'])
                        eSize = fill['size']
                        Product_id = fill['product_id']
                        lastFill = fill['order_id']

                        if fill['side'] == 'buy':
                            priceCheck = (fill['price'] + ' buy')
                            newSide = 'sell'

                        elif fill['side'] == 'sell':
                            priceCheck = (fill['price'] + ' sell')
                            newSide = 'buy'

                        roundFill = round(float(fill['price']), marketDec)
                        dictPrice = str(roundFill)
                        print("This is the dictPrice")
                        print(dictPrice)
                        stringFill = str(dictPrice)

                        print("This is the matrixDict")
                        pprint(matrixDict)
                        mdictKey = dictPrice + " " + fill['side']

                        print("This is mdictKey")
                        print(str(mdictKey))

                        floatPrice = float(fill['price'])
                        roundPrice = round(floatPrice , 2)

                        newKey = str(roundPrice) + " " + fill['side']
                        newPrice = matrixDict[mdictKey]

                        #peg = fill['price']

                        #rPeg = round(peg, marketDec)

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

                        r = requests.post(api_url + '/orders', json=engineOrder, auth=auth)

                        orderResponse = r.json()

                        #print("This is the order response default print")
                        #print(orderResponse)

                        print("This is the order response pretty print")
                        pprint(orderResponse)


                        count2 = count2 + 1
                        #jumpCount = jumpCount + 1

                time.sleep(5)

                if x is False:
                    print("Big loop break")
                    break















'''
        count2 = 0

        while count2 < 100:

            if jump[count2] == last_fill_dealt_withE:
                count2 = 101

            else:

                print(jump[count2])
                eOrderID = jump[count2]['order_id']
                eSide = jump[count2]['side']
                eSize = jump[count2]['size']
                ePrice = jump[count2]['price']
                eProduct_id = jump[count2]['product_id']

                if count2 == 0:
                    last_order_dealt_withN = eOrderID
                    last_order_file_handle2 = open(
                        '/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/last_order_id_processed.txt',
                        'w')
                    last_order_file_handle2.write(str(last_order_dealt_withN))

                print("This is matrixRead:")
                print(matrixRead[count2])

                for line5 in matrixRead:


                    #print("This is matrix price at index " + str(line5[0]))
                    #print(line5[1])
                    mIndex = line5[0]
                    mPrice = line5[1]
                    mVolume = line5[2]


                    if float(ePrice) == float(mPrice):
                        if eSide == 'buy':
                            newSide = 'sell'
                            newPeg = mIndex + 1
                            newPrice = matrixRead[newPeg][1]
                            print(newPrice)


                        elif eSide == 'sell':
                            newSide = 'buy'
                            newPeg = mIndex - 1
                            newPrice = matrixRead[newPeg][1]
                            print(newPrice)



                    engineOrder = {'side': newSide, 'size': eSize, 'price': newPrice, 'product_id': Product_id}

                    r = requests.post(api_url + '/orders', json=engineOrder, auth=auth)

            count2 += 1


'''
    
'''
    print(jump[0]['order_id'])
    secondID = 'b1b67a1d-5826-4890-a5f1-ec259c331932'
    if jump[0]['order_id'] == secondID :
        print('You win the night!')
'''
    #for line in jump:
    #    print(line)





'''
    if jump[0] != last_fill_dealt_withE:
        orderID = jump['order_id']
        side =  jump['side']
        size =  jump['size']
        price =  jump['price']
        product_id =  jump['product_id']
'''

    #print(requestFills[0]['order_id'])
#orderIds = []

##for key in requestFills.json():
   # orderID = key['order_id']
  #  side =  key['side']
 #   size =  key['size']
#    price =  key['price']
#    product_id =  key['product_id']
   # if key['order_id'] == last_fill_dealt_withE
  #      break
 #
#    print (orderID , side , size ,  price , product_id)

  #  fillInfo = [json.loads(orderID , side , size ,  price , product_id) for key in requestFills.results]

#    orderIds.append = fillInfo

    #docstats = [json.loads(doc['status']) for doc in response.results]

#print(orderIds)

'''

    while loopit == True:
        run_once = 0
        last_order_file_handle = open(
            '/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/last_order_id_processed.txt', 'r+')
        last_fill_dealt_with = last_order_file_handle.readline()
        print('this is the last order_id dealt with ' + last_fill_dealt_with)
        last_order_file_handle.close()

        f = requests.get(api_url + '/fills?cb-before=' + str(last_fill_dealt_with) + '&product_id=LTC-USD',
                         auth=auth)
        print(f.json())

        if run_once == 0:
            

        for key in f.json():

            wait = 0

            print('    this is the most recent order_id ' + key['order_id'])

            check_key = key['order_id']

            if str(key['order_id']) != last_fill_dealt_with:
                print('This order has triggered:')
                print(
                    key['price'], key['size'], key['fee'], key['side'], key['settled'], key['liquidity'],
                    key['created_at'],
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

                        last_order_file_handle2 = open(
                            '/Users/woodybrando/PycharmProjects/EdenMatrixTrading/GDAX/last_order_id_processed.txt',
                            'w')

                        last_order_file_handle2.write(str(last_fill_dealt_with2))

                        print(str(last_fill_dealt_with2))
                        last_order_file_handle2.close()
                        run_once = 1
                    break
            elif check_key == last_fill_dealt_with:
                print('No new trades... hold tight it will happen')

                time.sleep(10)





if activateEngine == n:
        exit()

'''