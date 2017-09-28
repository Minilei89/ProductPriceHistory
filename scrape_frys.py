from scrape_website import ScrapeWebsite
from datetime import datetime
import re
from time import sleep
from random import randint

class ScrapeFrys(ScrapeWebsite):
    def __init__(self, search_nearby=True):
        ScrapeWebsite.__init__(
            self,
            "http://www.frys.com/",
            "/search?search_type=regular&sqxts=1&cat=&query_string=",
            )
    self._format_search = '&nearbyStoreName='
    self._search_nearby = search_nearby

    def get_format_search():
        return self._format_search

    def get_search_nearby():
        return self._search_nearby

    def scrape_search(self, search):
        soup = self._generate_soup(
            self.get_base_url() +
            self.get_search_format() +
            search +
            self.get_format_search() +
            self.get_search_nearby())
        self.get_items(soup)

    def get_items(self, soup):
        prodCol = soup.find_all(id='prodCol')
        print(prodCol)


if __name__ == '__main__':
    TestScrape = ScrapeFrys(False)
    TestScrape.scrape_search(self, 'Intel')
