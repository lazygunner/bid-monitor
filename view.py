# -*- encoding:utf-8 -*-

import json
from threading import Thread

from flask import Flask, render_template, request
from flask_redis import Redis

from monitor import BidMonitor

REDIS_URL = "redis://@localhost:6379"
REDIS_DATABASE = 0

app = Flask(__name__)
redis_store = Redis(app)


@app.route('/')
def bid_status():
    auction_list = redis_store.get('auctions')
    bid_status_list = []
    if auction_list:
        auction_list = json.loads(auction_list)

        for auction in auction_list:
            url = auction['url']
            bottom_price = int(auction['bottomPrice'])
            bm = BidMonitor(url, bottom_price)
            bm.monitor()
            bid_status_dict = bm.analyze_statue()
            bid_status_list.append(bid_status_dict)

    return render_template('bid_status.html', bid_status_list=bid_status_list)


@app.route('/list', methods=['GET', 'POST'])
def auction_list():
    if request.method == 'POST':
        data = request.values.to_dict().get('auction_list', [])
        redis_store.set('auctions', data)
        auction_list = redis_store.get('auctions')
    else:
        auction_list = redis_store.get('auctions')

    if auction_list:
        auction_list = json.loads(auction_list)
    else:
        auction_list = []
    return render_template('list.html', auction_list=auction_list)


if __name__ == '__main__':
    app.debug = True
    app.run(port=8877)
