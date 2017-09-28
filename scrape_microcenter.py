from scrape_website import ScrapeWebsite
from datetime import datetime

class ScrapeMicrocenter(ScrapeWebsite):
    """
    Define the ScrapeMicrocenter object which inherits from ScrapeWebsite object
    """

    def __init__(self, search_local=False):
        """
        Initialize WebScrape object with the base url of microcenter.com and the
        search format used by the site. Creates search_attr_req which are the
        attr used to locate item of interest.
        :param search_local: boolean statement that determines whether scraper
        should search local.
        """
        ScrapeWebsite.__init__(self, "http://www.microcenter.com",
                           "/search/search_results.aspx?ntt=")
        self._search_attr_req = {'Url': 'href', 'ProductName':'data-name',
                                'ProductPrice':'data-price',
                                'Brand':'data-brand', 'Category':'data-category'
                                }
        self._search_local = search_local
        if not search_local:
            self._web_store = '&myStore=false'
        else:
            self._web_store = '&myStore=True'

    def __repr__(self):
        """
        Override WebScrape function to represent the MicrocenterScrape object.
        :return: Returns the string used to initialize the MicrocenterScrape
        object.
        """
        return 'MicrocenterScrape({})'.format(self.get_search_local)

    def get_search_attr_req(self):
        """
        Getter method for search_attr_req
        :return: Returns the list of attr used to identify product of interest
        """
        return self._search_attr_req

    def get_search_local(self):
        """
        Getter method for search_local variable.
        :return: Returns whether object searches locally or on the online store.
        """
        return self._search_local

    def scrape_SKU_mpn(self, url):
        """
        Function takes url of product and returns a unique SKU from the site and
        globally accepted mpn.
        :return: Returns the SKU used as dictionary key and mpn used for
        comparing products in other tables.
        """
        #sleep(randint(30, 60))
        assert type(url) == str, 'url must be of type str'
        soup = self._generate_soup(url)
        if soup != None:
            try:
                SKU = soup.find('dd', itemprop="sku").text.strip()
                mpn = soup.find('dd', itemprop="mpn").text.strip()
            except AttributeError as error:
                print(error)
                return None, None
        else:
            return None, None
        return SKU, mpn

    def recursive_page_scraper(self, url):
        """
        Function takes a url and compiles a list of products found that match
        the attribute requirements for product of interest. If so, calls
        scrape_SKU_mpn to obtain the SKU and manufacturing part number and adds
        them to the sql server
        :param url: Takes a microcenter search url and identifies products of
        interest. Using the products of interest's
        url, it obtains the SKU and mpn. Add item info to product dict
        :return: None
        """
        assert type(url) == str, 'url must be of type str'
        soup = self._generate_soup(url)
        if soup != None:
            list_a = soup.find_all('a')
            next_page = set()
            unique_product_url = set()
            for item in list_a:
                product_info = {}
                if all(attr in item.attrs for attr in self.get_search_attr_req().values()):
                    if self.get_base_url() + item.attrs[self.get_search_attr_req()['Url']] not in unique_product_url:
                        unique_product_url.add(self.get_base_url() +
                                               item.attrs[self.get_search_attr_req()['Url']])
                        SKU, mpn = self.scrape_SKU_mpn(self.get_base_url() + item.attrs[self.get_search_attr_req()['Url']])
                        if SKU:
                            product_info['Sku'] = SKU
                            for attr in self.get_search_attr_req():
                                if item.attrs[self.get_search_attr_req()[attr]]:
                                    product_info[attr] = item.attrs[self.get_search_attr_req()[attr]]
                                else:
                                    product_info[attr] = "NULL"
                            if mpn:
                                product_info['Mpn'] = mpn
                            else:
                                product_info['Mpn'] = 'NULL'
                            product_info['Time'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
                            product_info['Url'] = self.get_base_url() + product_info['Url']
                            yield product_info
                if '>' in item:  # If there is a next page, add url to next_page set
                    next_page.add(self.get_base_url() + item.attrs['href'])
        if next_page:
            yield from self.recursive_page_scraper(next_page.pop() + self._web_store)

    def scrape_search(self, search):
        """
        Takes a string that is used to search the Microcenter website. Adds
        products list to dictionary
        information.
        :param search: String argument
        :return: None
        """
        assert type(search) == str, 'search must be of type str'
        yield from self.recursive_page_scraper(self.get_base_url() +
                                    self.get_search_format() +
                                    search + self._web_store)
