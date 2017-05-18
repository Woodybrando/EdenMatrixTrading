#!/usr/bin/env python
'''
    Copyright (c) 2017 by Jayson Rahmlow <jayson.rahmlow@gmail.com>
      and Vanessa Rahmlow <vannyrahmlow@gmail.com>

    This file is part of EdenMatrixTrading.

    EdenMatrixTrading is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    EdenMatrixTrading is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with EdenMatrixTrading.  If not, see <http://www.gnu.org/licenses/>.
'''

import httplib
import urllib
import json
import hashlib
import hmac
import time
import requests

# Use these for testing or Replace with your own API key data
BTC_API_KEY = "4UJ8ZHCW-LIR3CGIJ-Y2GZAQ92-6CQ7W6IB-1WTYSZ98"
BTC_API_SECRET = "409431dc77f94b5046ff49343a3d24c852fe2b6bbc701162dda002fe03e30e2d"

# *******************************************************************************************************
# ******************* HARD CODE A MATRIX FOR QUICK AND EASY TEST CASE NMC/BTC ***************************
# *********************n REMOVE ALL THIS HARDCODE WHEN DONE TEST CASE **********************************
# *******************************************************************************************************

# matrix_nmc_usd = [0.5000,0.5095,0.5192,0.5290,0.5391,0.5493,0.5598,0.5704,0.5813,0.5923,0.6035,0.6150,0.6267,0.6386,0.6507,
#                   0.6631,0.6757,0.6885,0.7016,0.7150,0.7285,0.7424,0.7565,0.7709,0.7855,0.8004,0.8156,0.8311,0.8469,0.8630,
#                   0.8794,0.8961,0.9131,0.9305,0.9481,0.9662,0.9846,1.0033,1.0223,1.0417,1.0615,1.0817,1.1023,1.1232,
#                   1.1445,1.1663,1.1885,1.2110,1.2340,1.2575,1.2814,1.3057,1.3558,1.3816,1.4078,1.4346,1.4618,
#                   1.4896,1.5179,1.5467,1.5761,1.6061,1.6366,1.6677,1.6994,1.7317,1.7646,1.7981,1.8323,1.8671,
#                   1.9026,1.9387,1.9755,2.0130,2.0513,2.0903,2.1300,2.1705,2.2117,2.2537,2.2966,2.3402,2.3847,
#                   2.4300,2.4761,2.5232,2.5711,2.6200,2.6700,2.7205,2.7722,2.8248,2.8785,2.9332,2.9889,3.0457,
#                   3.1036,3.1626,3.2227,3.2839,3.3463,3.4099,3.4746,3.5407,3.6079,3.6765,3.7463,3.8175,3.8901,3.9640]

# matrix_trade_state = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
#                       0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
#                       0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

# *******************************************************************************************************
# ********************************* DEFINE FUNCTIONS *********************************************
# *******************************************************************************************************


def generate_matrix(start, end, percentage):
    """Generates the peg matrix and the corresponding trade state matrix."""
    current = start
    matrix = []
    while current <= end:
        matrix.append(current)
        current *= percentage

    trade_state = [0 for _ in matrix]

    return matrix, trade_state


def btce_signed_request(method, params):
    """Makes a signed request to the BTC-e API with the given method and parameters."""

    params["method"] = method
    params["nonce"] = int(round(time.time() - 1398621111, 1) * 10)

    h = hmac.new(BTC_API_SECRET, digestmod=hashlib.sha512)
    h.update(urllib.urlencode(params))

    trade_headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Key": BTC_API_KEY,
        "Sign": h.hexdigest(),
    }

    response = requests.post(
        "https://btc-e.com/tapi", headers=trade_headers, data=params)

    print '[%s] %s %s' % (method, response.status_code, response.reason)
    return response


def marketdepth(tpair, limit=150):
    """Returns a tuple containing (asks, bids)."""

    resp = requests.get(
        "https://btc-e.com/api/3/depth/" + tpair, params={"limit": limit})
    if resp.status_code == 200:
        data = resp.json()
        data = data.get(tpair)
        return data.get("asks"), data.get("bids")
    else:
        return None, None


def trade(tpair, rate, ttype, amount):
    """Adds a trade order to the exchange.  Returns a tuple with the values (success, order id)."""

    print "Trading tpair " + str(tpair) + " amount is " + str(
        amount) + " and type is " + str(ttype) + " rate is " + str(rate)
    resp = btce_signed_request("Trade", {
        "pair": tpair,
        "rate": rate,
        "type": ttype,
        "amount": amount,
    })

    if resp.status_code == 200:
        data = resp.json()
        success = data.get("success") == 1
        order_id = data.get("return", {}).get("order_id")
        return success, order_id
    else:
        return False, None


def cancelorder(order_id):
    """Returns True if the order was canceled successfully, False otherwise."""

    resp = btce_signed_request("CancelOrder", {"order_id": order_id})
    if resp.status_code == 200:
        data = resp.json()
        return data.get("success") == 1
    else:
        return False


def activeorders(tpair=None):
    """Returns an array of the user's active orders.  Optional tpair parameter specifies the trading pair."""

    params = {}
    if tpair is not None:
        params["pair"] = tpair

    resp = btce_signed_request("ActiveOrders", params)
    if resp.status_code == 200:
        data = resp.json()
        data = data.get("return")
        if data is None:
            return None

        # the data is returned as a dictionary, so we convert it to an array for convenience
        orders = []
        for order_id, order_data in data.iteritems():
            order_data[
                "order_id"] = order_id  # add the order_id to the returned order data
            orders.append(order_data)
        return orders
    else:
        return None


def tradehistory(tpair=None):
    """Returns an array of the user's trades.  Optional tpair parameter specifies the trading pair."""

    params = {}
    if tpair is not None:
        params["pair"] = tpair

    resp = btce_signed_request("TradeHistory", params)

    if resp.status_code == 200:
        data = resp.json()
        data = data.get("return")
        if data is None:
            return None

        # the data is returned as a dictionary, so we convert it to an array for convenience
        trades = []
        for trade_id, trade_data in data.iteritems():
            trade_data[
                "trade_id"] = trade_id  # add the trade_id to the returned trade data
            trades.append(trade_data)
        return trades
    else:
        return None


def round_tpair_price(number, tpair):
    return_number = 0
    if tpair == "nmc_usd":
        return_number = round(number, 2)
    else:
        print "ERROR!! Haven't defined round price function for tpair " + tpair
    return return_number


def round_tpair_volume(number, tpair):
    return_number = 0
    if tpair == "nmc_usd":
        return_number = round(number, 4)
    else:
        print "ERROR!! Haven't defined round volume function for tpair " + tpair
    return return_number


# Generate the matrix of pegs (and the corresponding trading state matrix)
matrix_bottom = .5000
matrix_top = 3.9640
matrix_nmc_usd, matrix_trade_state = generate_matrix(matrix_bottom, matrix_top,
                                                     1.019)

print "=== NMC/USD market depth:"
asks, bids = marketdepth("nmc_usd")
print "Asks:", asks
print ""
print "Bids:", bids

print ""
print "=== Trade history:"
for trade in tradehistory():
    print trade

print ""
print "=== Active orders:"
#for order in activeorders("nmc_usd"):
#    print order

# *******************************************************************************************************
# ********************************* END OF DEFINE FUNCTIONS *********************************************
# *******************************************************************************************************

# BTC-E MARKET FEE
btc_e_trade_fee = .002

# WHAT AMOUNT OF FIAT ($, EURO, YUAN, YEN) ARE YOU OKAY WITH GIVING UP FOREVER
# TO LEARN FROM THIS EXPERIENCE? What is initial investment amount?

# EDEN STORE VALUE: (USER INITIAL INVESTMENT)
# initial_investment_usd
# JAYSON AND VANNYCAT IF WE ARE GOING NMC TO LTC THIS SHOULDNT BE USE
# ----------> PLEASE CHANGE
initial_investment_usd = 16.50
initial_setup_fee = initial_investment_usd * btc_e_trade_fee
initial_investment_usd -= initial_setup_fee

# EDEN: DISPLAY: "WE WILL CALL THIS YOUR INITIAL INVESTMENT"

# WHAT MARKET WOULD YOU LIKE TO TRADE IN: BTC-E, GDAX, POLONIEX
# PRESS HERE TO LEARN MORE ABOUT EACH EXCHANGE
# exchange_choice
exchange_choice = "btc-e.com"

# USER XCHANGE: BTC-E

# WHAT CURRENCY PAIR WOULD YOU LIKE TO TRADE IN
# USER PAIR Example: LTC/USD
# tpair
tpair = "nmc_usd"

# ***********************************************************************************************************
# ----------> JAYSON AND VANNY THIS CALL TO GET CURRENT MARKET PRICE IS COMMENTED OUT UNTIL WE HAVE INTERNET
# ***********************************************************************************************************

# EDEN: CALL TO (exchange_choice) ASK FOR (tpair) Current Market PRICE
# current_tpair_mprice

if exchange_choice == "btc-e.com":
    depth = marketdepth(tpair, 5)
    if depth is None:
        print "Error connecting to btc-e.com"
        exit(1)

    # Debug make sure these asks look appropriate
    current_tpair_mprice = depth[0][4]

    # In case we need to write out a scratch version
    # f = open("/Users/ApplejackFilms-mbp/Documents/Eden-Project/DepthTest.txt", "w")
    # f.write(str(dict))

    # EDEN: DISPLAY (CURRENT MARKET PRICE): LTC/USD = 15
    # Debug print the market price for us to buy the currency
    print str(current_tpair_mprice)

else:
    print "We don't have software created for markets other than btc-e yet. Stay tuned!"
    current_tpair_mprice = 0
    #exit 1

# REMOVE THIS COMMENTING OUT AND QUERY MARKET FOR CURRENT MARKET PRICE WHEN INTERNET

# ***********************************************************************************************************
# -----> VANNYCAT AND JAYSON REMOVE THIS HARDCODE WHEN OFF OF THE TEST CASE
# ***********************************************************************************************************

current_tpair_mprice = 2

#### this needs to be that grabs this from the api

# EDEN ASK: WHAT PERCENT OF INVESTMENT TO BE PUT IN MOON BASKET/MATRIX - .1, .3, .5?
# Moon basket is a long term hold goal (say you want to pay off a credit card, or a car loan, how @ what price would it take)
# moon_bucket_factor
# example: MOONBASKET FACTOR = .3
# this is what could be a user defined
moon_bucket_factor = .3

# EDEN CALC: (initial_investment_usd)*(moon_bucket_factor) = (moon_basket_current_market_buy_amount) = 300
# moon_basket_current_market_buy_amount# VANNYCAT AND JAYSON NOT USD!
moon_basket_current_market_buy_amount = initial_investment_usd * moon_bucket_factor

# Set the price of the Moonbasket Sell to one peg above the matrix
moon_basket_peg = round_tpair_price((matrix_top * 1.019), "nmc_usd")

# you're matrix won, now what do you want to do with your money

# EDEN: WHAT RATIO OF MATRIX WOULD YOU LIKE TO CHOOSE 60/40 65/35?
# EDEN: EXPLANATION OF BENEFIT OR MARKET CONDITIONS EACH APPROPIATE FOR
matrix_investment = initial_investment_usd - moon_basket_current_market_buy_amount

# this is where we take our remaining $700 (non moon basket) investment and split it in to 2
# $350 would go into a current market buy, those coins would be spread into a peg spread from 1 peg above market to 2 * current market
# $350 would go into buys @ below market peg spreads down to .5 of current market.
# this gives our buys more volume to protect against a falling market price
# this gives our sells less volume but more of a spread and great value for selling off new coins
# USER MATRIX BELOW: .50
# USER MATRIX ABOVE: .50

# .5 * matrix_investment = below_market_buy
# .5 * matrix_investment = above_market_buy
below_market_buy = matrix_investment * .5
above_market_buy = matrix_investment * .5
above_market_coin_count = above_market_buy / current_tpair_mprice

number_of_nmc_usd_pegs = len(matrix_nmc_usd)

starting_tpair_coins = matrix_investment / current_tpair_mprice
nmc_usd_trade_volume = starting_tpair_coins / number_of_nmc_usd_pegs
nmc_usd_trade_volume = round_tpair_volume(nmc_usd_trade_volume, "nmc_usd")

# Uncomment this out when the printout looks good
# EDEN: (current_tpair_mprice)/(moon_basket_current_market_buy_amount) = (moonbasket_coins_count) 20
moonbasket_coins_count = moon_basket_current_market_buy_amount / current_tpair_mprice
moonbasket_coins_count = round_tpair_volume(moonbasket_coins_count, "nmc_usd")

# EDEN: BUY (moonbasket_coins_count) @ (current_tpair_mprice)
# EDEN: AND CONFIRM TRANSACTION
# EDEN: AND CALCULATE THE FEES PAID FOR THE TRANSACTION
#if (exchange_choice == "btc-e.com"):
#    trade_success, order_id = trade(tpair, current_tpair_mprice, "buy", moonbasket_coins_count)
#    print "Purchased moonbucket " + str(moonbasket_coins_count) + " coins at price " + str(current_tpair_mprice)
#    if (trade_success != 777):
#        print "Error Buying Moonbasket coins at market price " + current_tpair_mprice

# EDEN: SET MOONBASKET GOAL SELLS (moonbasket_coins_count @ one peg above matrix top)
# EDEN CREATE SELL moonbasket_coins_count @ moon_basket_peg
if exchange_choice == "btc-e.com":
    trade(tpair, moonbasket_coins_count, "sell", moon_basket_peg)
    print "Put moonbasket sell trade in. Selling " + str(
        moonbasket_coins_count) + "coins of NMC at price " + str(
            moon_basket_peg)

exit(1)

# Buy Initial Matrix Investment
# trade_success, order_id = trade(tpair, current_tpair_mprice, "buy", above_market_coin_count)
# print "Purchased initial investment " + str(above_market_coin_count) + " coins at price " + str(current_tpair_mprice)
#if (trade_success != 777):
#    print "Error Buying Above Market Coin Count (Initial Buy) "

# For each peg ask is this peg less than the market price we paid by an amount > the spread of 1.9% (rounded up)
# if so then place a buy at our static volume and
# store the value 1 in our matrix_peg_state (is this the right name?)
# if peg value is greater than market price we paid by 1.9%
# set a sell at our static volume till one below our top peg and
# store the value 2 in our matrix_peg_state
# also for peg <= spread below market
# set matrix_peg_state to 0
# store trade id in matrix_trade_id in index equal to peg index #

list_counter = 0
print str(number_of_nmc_usd_pegs)
for peg in matrix_nmc_usd:
    if peg < current_tpair_mprice:
        if (peg * 1.019) < current_tpair_mprice:
            trade("nmc_usd", peg, "buy", nmc_usd_trade_volume)
            matrix_trade_state[list_counter] = 1
            print "Buy order for " + str(
                nmc_usd_trade_volume) + "NMC at price " + str(peg)
        else:
            print "No orders at peg " + str(peg)
            matrix_trade_state[list_counter] = 0
    elif peg == current_tpair_mprice:
        print "No orders at peg " + str(peg)
        matrix_trade_state[list_counter] = 0
    else:
        if (peg * .995) > current_tpair_mprice:
            trade("nmc_usd", peg, "sell", nmc_usd_trade_volume)
            matrix_trade_state[list_counter] = 2
            print "Sell order for " + str(
                nmc_usd_trade_volume) + "NMC at price " + str(peg)
        else:
            print "No orders at peg " + str(peg)
            matrix_trade_state[list_counter] = 0
    list_counter += 1

# ***************************************************************************************************
# *********** CODE WRITTEN 5/12 BY VANNYCAT TO GET RID OF OLD BTC/LTC BUY ORDER AND TO **************
# ******************* SET UP THE NMC/BTC MATRIX WITH ABOVE HARD CODED MATRIX ************************
# ***************************************************************************************************
'''
# Now constantly monitor to get the trade history. For every buy, create a sell order up one peg, for every sell,
# create a buy order down a peg
# number_of_trades = tradehistory("nmc_usd")
tradenum = 0
while tradenum < number_of_trades:

    print "This is " + str(tradenum)

    # ******** Jayson and Vanny - find out how to get at the data in the tradehistory and react accordingly ****
'''
