# -*- encoding:utf-8 -*-
import re

import requests
from lxml import html

user_agent = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)'
              'AppleWebKit/537.36 (KHTML, like Gecko)'
              'Chrome/39.0.2171.95 Safari/537.36')


class BidMonitor(object):

    def __init__(self, url, bottom_price):
        self.xpaths = {}
        self.bid_status_dict = {}
        self.url = url
        self.bottom_price = bottom_price
        self._init_xpath()
        pass

    def _init_xpath(self):
        # 名称
        self.xpaths['name'] = '//div[@class="pm-main"]/div/div[2]/h1/text()'
        # 当前价格
        self.xpaths['price_now'] = '//div[@class="pm-money"]/span/span/text()'
        pm_attach_xpath = ('//div[@class="pm-attachment"]'
                           '/ul[%d]/li[@class="line%d"]/span[2]/text()')
        # 起拍价
        self.xpaths['start_price'] = pm_attach_xpath % (1, 1)
        # 加价幅度
        self.xpaths['raise_price'] = pm_attach_xpath % (1, 2)
        # 保证金
        self.xpaths['ensure_money'] = pm_attach_xpath % (1, 3)

        # 参与人数
        self.xpaths['bidder_count'] = '//div[@class="pm-people"]/span[1]/em/text()'

    def _parse_price(self, price_str_raw):
        price = ''
        for price_str in price_str_raw.split(','):
            price += price_str
        return int(price)

    def _get_xpath_value(self, tree, param_name, xpath_str):
        value_list = tree.xpath(xpath_str)
        if value_list == []:
            print '[%s] parse xpath error!' % param_name
            return -1

        if param_name == 'price_now':
            value_raw = value_list[0]
            p = re.compile(r'\r\n\t*(.*?)\r\n')
            price_now_list = p.findall(value_raw)
            if len(price_now_list) == 0:
                print 're get price_now error!'
            value = self._parse_price(price_now_list[0])
        elif param_name == 'name':
            value = value_list[0]
        else:
            value = self._parse_price(value_list[0])

        return value

    def monitor(self):
        headers = {
            'User-Agent': user_agent
        }
        page = requests.get(self.url, headers=headers)
        tree = html.fromstring(page.text)

        value_dict = {}
        for param, xpath_str in self.xpaths.items():
            value_dict[param] = self._get_xpath_value(tree, param, xpath_str)

        value_dict['url'] = self.url
        value_dict['bottom_price'] = self.bottom_price
        self.bid_status_dict = value_dict
        return value_dict

    def analyze_statue(self):
        price_now = self.bid_status_dict['price_now']
        raise_price = self.bid_status_dict['raise_price']
        remain_count = (self.bottom_price - price_now) / float(raise_price)
        if remain_count <= 0:
            status = 'ok'
        elif remain_count > 0 and remain_count < 10:
            status = 'warn'
        else:
            status = 'danger'

        self.bid_status_dict['status'] = status
        return self.bid_status_dict


if __name__ == '__main__':
    m = BidMonitor('http://paimai.taobao.com/pmp_item/42989439241.htm')
    print m.monitor()
