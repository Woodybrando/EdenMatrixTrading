
import urllib
import hashlib
import hmac
import requests

class BtceExchange:
    def __init__(self, api_key, api_secret, trade_fee):
        self.api_key = str(api_key)
        self.api_secret = str(api_secret)
        self.trade_fee = trade_fee


    def signed_request(self, method, params):
        """Makes a signed request to the BTC-e API with the given method and parameters."""

        params["method"] = method
        params["nonce"] = int(round(time.time() - 1398621111, 1) * 10)

        h = hmac.new(self.api_secret, digestmod=hashlib.sha512)
        h.update(urllib.urlencode(params))

        trade_headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Key": self.api_key,
            "Sign": h.hexdigest(),
        }

        response = requests.post("https://btc-e.com/tapi", headers=trade_headers, data=params)

        print '[%s] %s %s' % (method, response.status_code, response.reason)
        return response


    def marketprice(self, tpair):
        depth = self.marketdepth(tpair, 5)
        if depth is None:
            die("Error fetching market depth")

        asks, bids = depth

        # Debug make sure these asks look appropriate
        price = asks[4][0]
        return price


    def marketdepth(self, tpair, limit=150):
        """Upon failure, returns None.  Upon success, returns a tuple containing (asks, bids)."""

        resp = requests.get("https://btc-e.com/api/3/depth/" + tpair, params={"limit": limit})
        if resp.status_code == 200:
            data = resp.json()
            data = data.get(tpair)
            return data.get("asks"), data.get("bids")
        else:
            return None


    def trade(self, tpair, rate, ttype, amount):
        """Adds a trade order to the exchange.  Returns a tuple with the values (success, order id)."""

        print "Trading tpair " + str(tpair) + " amount is " + str(amount) + " and type is " + str(ttype) + " rate is " + str(rate)

        resp = self.signed_request("Trade", {
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


    def cancelorder(self, order_id):
        """Returns True if the order was canceled successfully, False otherwise."""

        resp = self.signed_request("CancelOrder", {"order_id": order_id})
        if resp.status_code == 200:
            data = resp.json()
            return data.get("success") == 1
        else:
            return False


    def activeorders(self, tpair=None):
        """Returns an array of the user's active orders.  Optional tpair parameter specifies the trading pair."""

        params = {}
        if tpair is not None:
            params["pair"] = tpair

        resp = self.signed_request("ActiveOrders", params)
        if resp.status_code == 200:
            data = resp.json()
            data = data.get("return")
            if data is None:
                return None

            # the data is returned as a dictionary, so we convert it to an array for convenience
            orders = []
            for order_id, order_data in data.iteritems():
                order_data["order_id"] = order_id  # add the order_id to the returned order data
                orders.append(order_data)
            return orders
        else:
            return None


    def tradehistory(self, tpair=None, count=None):
        """Returns an array of the user's trades.  Optional tpair parameter specifies the trading pair."""

        params = {}
        if tpair is not None:
            params["pair"] = tpair
        if count is not None:
            params["count"] = count

        resp = self.signed_request("TradeHistory", params)

        if resp.status_code == 200:
            data = resp.json()
            data = data.get("return")
            if data is None:
                return None

            # the data is returned as a dictionary, so we convert it to an array for convenience
            trades = []
            for order_id, trade_data in data.iteritems():
                trade_data["order_id"] = order_id  # add the order_id to the returned trade data
                trades.append(trade_data)
            return trades
        else:
            return None