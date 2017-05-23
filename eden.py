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
import hashlib
import hmac
import time
import requests
from utils import *

# Use these for testing or Replace with your own API key data
# BTC_API_KEY = "4UJ8ZHCW-LIR3CGIJ-Y2GZAQ92-6CQ7W6IB-1WTYSZ98"
# BTC_API_SECRET = "409431dc77f94b5046ff49343a3d24c852fe2b6bbc701162dda002fe03e30e2d"

config = read_config()

# *******************************************************************************************************
# ********************************* DEFINE FUNCTIONS *********************************************
# *******************************************************************************************************

def round_tpair_price(number, tpair):
    return_number = 0
    if tpair == "nmc_usd":
        return_number = round(number, 2)
    elif tpair == "ltc_usd":
        return_number = round(number, 2)
    else:
        print "ERROR!! Haven't defined round price function for tpair " + tpair
    return return_number


def round_tpair_volume(number, tpair):
    return_number = 0
    if tpair == "nmc_usd":
        return_number = round(number, 4)
    elif tpair == "ltc_usd":
        return_number = round(number, 4)
    else:
        print "ERROR!! Haven't defined round volume function for tpair " + tpair
    return return_number


def generate_matrix(start, end, percentage, tpair):
    """Generates the peg matrix and the corresponding trade state matrix."""
    current = start
    matrix = []
    while current <= end:
        matrix.append(current)
        current *= percentage
        current = round_tpair_price(current, tpair)

    trade_state = [0 for _ in matrix]

    return matrix, trade_state


def btce_signed_request(method, params):
    """Makes a signed request to the BTC-e API with the given method and parameters."""

    params["method"] = method
    params["nonce"] = int(round(time.time() - 1398621111, 1) * 10)

    h = hmac.new(config["BTCE_API_SECRET"], digestmod=hashlib.sha512)
    h.update(urllib.urlencode(params))

    trade_headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Key": config["BTCE_API_KEY"],
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


# *******************************************************************************************************
# ********************************* END OF DEFINE FUNCTIONS *********************************************
# *******************************************************************************************************

# WHAT MARKET WOULD YOU LIKE TO TRADE IN: BTC-E, GDAX, POLONIEX
# PRESS HERE TO LEARN MORE ABOUT EACH EXCHANGE
# exchange_choice = "btc-e.com"

# USER XCHANGE: BTC-E

# WHAT CURRENCY PAIR WOULD YOU LIKE TO TRADE IN
# USER PAIR Example: LTC/USD
# tpair
# tpair = "nmc_usd"


# BTC-E MARKET FEE
# btce_trade_fee = .002

# Generate the matrix of pegs (and the corresponding trading state matrix)
# matrix_bottom = 1.4
# matrix_top = 3
# matrix_spread_percent = 1.019

matrix, matrix_trade_state = generate_matrix(config["matrix_bottom"], config["matrix_top"],
                                                     config["matrix_spread_percent"], config["tpair"])


# EDEN open file to record initial purchases and Matrix information
file = open("/Users/ApplejackFilms-mbp/Documents/Eden-Project/GitHub/Scratch/NMC_USD_Matrix", 'w')


# WHAT AMOUNT OF FIAT ($, EURO, YUAN, YEN) ARE YOU OKAY WITH GIVING UP FOREVER
# TO LEARN FROM THIS EXPERIENCE? What is initial investment amount?

# EDEN STORE VALUE: (USER INITIAL INVESTMENT)
# initial_investment_usd
# initial_investment_usd = 15
initial_investment_usd = config["initial_investment_usd"]
initial_setup_fee = initial_investment_usd * config["btce_trade_fee"]
initial_investment_usd -= initial_setup_fee

# EDEN: DISPLAY: "WE WILL CALL THIS YOUR INITIAL INVESTMENT"


# ***********************************************************************************************************
# Get Current Market Price
# ***********************************************************************************************************

if config["exchange_choice"] == "btc-e.com":
    depth = marketdepth(config["tpair"], 5)
    if depth is None:
        print "Error connecting to btc-e.com"
        exit(1)

    # Debug make sure these asks look appropriate
    current_tpair_mprice = depth[0][4][0]

else:
    print "We don't have software created for markets other than btc-e yet. Stay tuned!"
    current_tpair_mprice = 0
    #exit 1


# ***********************************************************************************************************
# EDEN ASK: WHAT PERCENT OF INVESTMENT TO BE PUT IN MOON BASKET/MATRIX - .1, .3, .5?
# ***********************************************************************************************************

# Moon basket is a long term hold goal (say you want to pay off a credit card, or a car loan, how @ what price would it take)
# moon_basket_factor
# example: MOONBASKET FACTOR = .3
# this is what could be a user defined
# moon_basket_factor = .3

# EDEN CALC: (initial_investment_usd)*(moon_basket_factor) = (moon_basket_current_market_buy_amount) = 300
# moon_basket_current_market_buy_amount# VANNYCAT AND JAYSON NOT USD!
moon_basket_current_market_buy_amount = initial_investment_usd * config["moon_basket_factor"]

# Set the price of the Moonbasket Sell to one peg above the matrix
moon_basket_peg = round_tpair_price((config["matrix_top"] * config["matrix_spread_percent"]), config["tpair"])


# you're matrix won, now what do you want to do with your money


# Uncomment this out when the printout looks good
# EDEN: (current_tpair_mprice)/(moon_basket_current_market_buy_amount) = (moonbasket_coins_count) 20
moonbasket_coins_count = moon_basket_current_market_buy_amount / current_tpair_mprice
moonbasket_coins_count = round_tpair_volume(moonbasket_coins_count, config["tpair"])

# EDEN: BUY (moonbasket_coins_count) @ (current_tpair_mprice)
# EDEN: AND CONFIRM TRANSACTION
#trade_success, order_id = trade(tpair, current_tpair_mprice, "buy", moonbasket_coins_count)
file.write("Purchased moonbucket " + str(moonbasket_coins_count) + " coins at price " +
           str(current_tpair_mprice) + "\n")

# EDEN: SET MOONBASKET GOAL SELLS (moonbasket_coins_count @ one peg above matrix top)
# EDEN CREATE SELL moonbasket_coins_count @ moon_basket_peg
trade_success, order_id = trade(config["tpair"], moon_basket_peg, "sell", moonbasket_coins_count)
file.write("Moonbasket Sell Order established " + str(moonbasket_coins_count) + "coins to sell at price "
           + str(moon_basket_peg) + '\n')



#############################################################################################################
# Buy Initial Matrix Investment
############################################################################################################
# EDEN: WHAT RATIO OF MATRIX WOULD YOU LIKE TO CHOOSE 60/40 65/35?
# EDEN: EXPLANATION OF BENEFIT OR MARKET CONDITIONS EACH APPROPIATE FOR
matrix_investment = initial_investment_usd - moon_basket_current_market_buy_amount

# this is where we take our remaining $700 (non moon basket) investment and split it in to 2
# $350 would go into a current market buy, those coins would be spread into a peg spread from 1 peg above market to 2 * current market
# $350 would go into buys @ below market peg spreads down to .5 of current market.
# this gives our buys more volume to protect against a falling market price
# this gives our sells less volume but more of a spread and great value for selling off new coins
below_market_buy = matrix_investment * .5
above_market_buy = matrix_investment * .5
above_market_coin_count = round_tpair_volume(above_market_buy / current_tpair_mprice, config["tpair"])
number_of_pegs = len(matrix)

starting_tpair_coins = matrix_investment / current_tpair_mprice
trade_volume = starting_tpair_coins / number_of_pegs
trade_volume = round_tpair_volume(trade_volume, config["tpair"])

#trade_success, order_id = trade(tpair, current_tpair_mprice, "buy", above_market_coin_count)
file.write("Initial investment: Purchased " + str(above_market_coin_count) + " coins at price "
           + str(current_tpair_mprice) + '\n')
file.write("Trade volume is " + str(trade_volume) + "at each peg")



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
print str(number_of_pegs)
for peg in matrix:
    if peg < current_tpair_mprice:
        if (peg * config["matrix_spread_percent"]) < current_tpair_mprice:
            trade(config["tpair"], peg, "buy", trade_volume)
            matrix_trade_state[list_counter] = 1
            file.write("Buy " + str(trade_volume) + "Coins at price " + str(peg) + "\n")
        else:
            matrix_trade_state[list_counter] = 0
    elif peg == current_tpair_mprice:
        matrix_trade_state[list_counter] = 0
    else:
        if (peg - (peg * config["matrix_spread_percent"])) <= current_tpair_mprice:
            trade(config["tpair"], peg, "sell", trade_volume)
            matrix_trade_state[list_counter] = 2
            file.write("Sell " + str(trade_volume) + "Coins at price " + str(peg) + "\n")
        else:
            matrix_trade_state[list_counter] = 0
    list_counter += 1

# ***************************************************************************************************
# *********** CODE WRITTEN 5/12 BY VANNYCAT TO GET RID OF OLD BTC/LTC BUY ORDER AND TO **************
# ******************* SET UP THE NMC/BTC MATRIX WITH ABOVE HARD CODED MATRIX ************************
# ***************************************************************************************************
'''
# Now constantly monitor to get the trade history. For every buy, create a sell order up one peg, for every sell,
# create a buy order down a peg
# number_of_trades = tradehistory("ltc_usd")
tradenum = 0
while tradenum < number_of_trades:

    print "This is " + str(tradenum)

    # ******** Jayson and Vanny - find out how to get at the data in the tradehistory and react accordingly ****
'''

# Next to do
# A daily coin free coin counter
# Since investors are so Value based when looking at performance
# we need a new coin counter to track how much new coin we've made today
# so for NMC today I've made 6 new NMC
# Original buy got me say 100, now I have 106 for the same initial investment
# So say the overall value has gone down from $200 to $180
# The investor should appreciate that they only initially got 100
# NMC for their initial investment
# They can now sell 6 coins without affecting their
# initial investment