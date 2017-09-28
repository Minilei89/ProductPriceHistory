from scrape_website import ScrapeWebsite
from datetime import datetime
import re
from time import sleep
from random import randint
import requests
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
print(s.getsockname()[0])
s.close()


class ScrapeBestBuy(ScrapeWebsite):
    def __init__(self):
        ScrapeWebsite.__init__(self, "https://www.bestbuy.com",
                            "/site/searchpage.jsp?st=")
        self._search_attr_req = {'Url': 'data-url',
                                'ProductName':'data-name',
                                'ProductPrice':'data-price',
                                'Sku': 'data-sku-id',
                                }
        self._search_features = '&_dyncharset=UTF-8&id=pcat17071&type=page&sc=Global&cp=1&nrp=&sp=&qp=&list=n&af=true&iht=y&usc=All+Categories&ks=960&keys=keys'

    def get_search_features(self):
        return self._search_features

    def get_search_attr_req(self):
        """
        Getter method for search_attr_req
        :return: Returns the list of attr used to identify product of interest
        """
        return self._search_attr_req

    def scrape_search(self, search):
        soup = self._generate_soup(self.get_base_url() +
                                self.get_search_format() +
                                search +
                                self.get_search_features())

        while True:
            sleep(randint(1,30))
            next_page = None
            yield from self.get_items(soup)
            next_page = self.get_next_page(soup)
            print(next_page)
            if next_page == '':
                break
            soup = self._generate_soup(next_page)

    def get_items(self, soup):
        list_item = soup.find_all('div', class_="list-item")
        counter = 0
        for item in list_item:
            counter += 1
            product_info = {}
            for sql_col, attr in self.get_search_attr_req().items():
                try:
                    product_info[sql_col] = item[attr]
                except KeyError as error:
                    print(error)
                    product_info[sql_col] = "NULL"
            brand = re.search('(?:{"brand":")(.*)"}', item['data-brand'])

            if brand == None:
                product_info['Brand'] = 'NULL'
            else:
                product_info['Brand'] = brand.group(1)
            price = re.search('^(\d)*(\.)?(\d\d)?', product_info['ProductPrice'])


            if price == None:
                pass
            elif price.group(1) != None and price.group(2) == None:
                product_info['ProductPrice'] = product_info['ProductPrice'] + '.00'

            model = item.find(itemprop="model")

            if model:
                product_info['Mpn'] = model.get_text()
            else:
                product_info['Mpn'] = 'Null'

            product_info['Url'] = self.get_base_url() + product_info['Url']
            product_info['Time'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
            print(product_info)
            yield product_info

    def get_next_page(self, soup):
        next_page = soup.find(title='Next Page')
        if next_page != None:
            return next_page['href']
        else:
            return None

if __name__ == "__main__":
    TestScrape = ScrapeBestBuy()
    for item in TestScrape.scrape_search("Intel"):
        print(item)
