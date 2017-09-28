import requests
import lxml
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from time import sleep
from random import randint
class ScrapeWebsite:
    """
    Define the ScrapeWebsite that contains the base url and search format
    needed to scrape the products on a website.
    """
    def __init__(self, base_url, search_format):
        """
        Initilizes object with the base url and search format needed to scrape
        the website for products.
        """
        self._base_url = base_url # base url for website to scrape
        self._search_format = search_format # search url

    def __str__(self):
        """
        Returns the url needed to search the website.
        """
        return self._base_url + self._search_format

    def __repr__(self):
        """
        Returns the str definition of the Scrape_Website object
        """
        return 'ScrapeWebsite(self, {}, {})'.format(self._base_url,
                                                    self._search_format)

    def _generate_soup(self, url):
        """
        Create BeautifulSoup object from url and return the generated object
        """
        assert isinstance(url, str), 'url must be of type str'
        sleep(randint(1,3))
        ua = UserAgent()
        user = ua.random
        headers = {"User-Agent":'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
        got_url = False
        try:
            page = requests.get(url, headers=headers)
            got_url = True
            soup = BeautifulSoup(page.text, 'lxml')
        except ConnectionError as error:
            print(error)
            soup = None
        return soup

    def get_base_url(self):
        return self._base_url

    def get_search_format(self):
        return self._search_format
