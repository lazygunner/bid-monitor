# -*- encoding:utf-8 -*-
import json
import logging
import logging.config

from flask import Flask, render_template, request, jsonify
from flask_redis import Redis

from monitor import BidMonitor


logging.config.fileConfig('logging.conf')
# create logger
logger = logging.getLogger('bidMonitor')

REDIS_URL = "redis://@localhost:6379"
REDIS_DATABASE = 0

app = Flask(__name__)
redis_store = Redis(app)

UPLOAD_FOLDER = '/tmp/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'csv'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    auction_list = redis_store.get('auctions')
    if auction_list:
        auction_list = json.loads(auction_list)
    else:
        auction_list = []

    error = 0
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            # filename = file.filename
            # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            url_list = ([auction['url'] for auction in auction_list])
            try:
                for line in file.readlines():
                    values = line.split(',')
                    if values[0] in url_list:
                        continue
                    auction_list.append({
                        'url': values[0],
                        'bottomPrice': values[1]
                    })

                redis_store.set('auctions', json.dumps(auction_list))
            except Exception:
                error = -1

    return jsonify({'error': error})


def _get_bid_status(auction):
    url = auction['url']
    bottom_price = float(auction['bottomPrice'])
    bm = BidMonitor(url, bottom_price)
    bm.monitor()
    bid_status_dict = bm.analyze_statue()

    return bid_status_dict


@app.route('/')
def bid_status():

    auction_list = redis_store.get('auctions')
    bid_status_list = []
    if auction_list:
        auction_list = json.loads(auction_list)

        try:
            for auction in auction_list:
                bid_status_list.append(_get_bid_status(auction))
        except Exception as e:
            logger.exception(e)

    return render_template('bid_status.html', bid_status_list=bid_status_list)


@app.route('/list', methods=['GET', 'POST'])
def auction_list():
    if request.method == 'POST':
        data = request.values.to_dict().get('auction_list', [])
        redis_store.set('auctions', data)

    auction_list = redis_store.get('auctions')
    if auction_list:
        auction_list = json.loads(auction_list)
    else:
        auction_list = []
    return render_template('list.html', auction_list=auction_list)


@app.route('/delete', methods=['GET', 'POST'])
def delete_all():
    redis_store.delete('auctions')

    return render_template('list.html', auction_list=[])


@app.route('/gap_level', methods=['POST', 'GET'])
def update_gap_level():
    gap_level1 = 0
    if request.method == 'POST':
        gap_dict = request.values.to_dict().get('gap_dict', {})
        gap_level1 = int(json.loads(gap_dict).get("gap_level1", 10))
        redis_store.set('gap_level1', gap_level1)
    elif request.method == 'GET':
         gap_level1 = redis_store.get('gap_level1') or 0
    print gap_level1
    return jsonify({'gap_level1': gap_level1})

if __name__ == '__main__':
    app.debug = True
    app.run(port=8888)
