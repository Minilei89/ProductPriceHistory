from scrape_website import ScrapeWebsite
from datetime import datetime
import re

class ScrapeBHPhoto(ScrapeWebsite):
    def __init__(self):
        ScrapeWebsite.__init__(self, "https://www.bhphotovideo.com", "/c/search?Ntt=")

    def scrape_prod_detail(self, soup):
        product_soup = soup.find_all(attrs={"data-selenium": "itemDetail"})
        product_data = {}
        for product in product_soup:
            product_name = product.find(attrs={"data-selenium":"itemHeadingLink"})
            product_data['Url'] = product_name.attrs['href']

            try:
                product_data['Brand'] = product_name.find(itemprop='brand').get_text()
            except AttributeError as error:
                product_data['Brand'] = 'NULL'

            product_data['ProductName'] = product_name.find(itemprop='name').get_text()
            try:
                product_data['Mpn'] = product.find(class_="mfrBullet").find(class_="sku").get_text()
            except AttributeError as error:
                product_data['Mpn'] = 'NULL'
            try:
                product_data['Sku'] = re.search('"sku":"([\d]+)"', product["data-itemdata"]).group(1)
            except:
                product_data['Sku'] = 'NULL'
            try:
                product_data['ProductPrice'] = product.find(attrs={"data-selenium":"price"}).get_text().strip()[1:].replace(',', '')
            except AttributeError as error:
                product['ProductPrice'] = 'NULL'

            product_data['Time'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
            if len(product_data.keys()) == 7:
                yield product_data

    def get_next_page(self, soup):
        if soup.find(class_="pn-next pn-btn fifteen litGrayBtn") != None:
            return soup.find(class_="pn-next pn-btn fifteen litGrayBtn")['href']

    def scrape_search(self, search):
        assert type(search) == str, 'url must be of type str'
        search_url = self.get_base_url() + self.get_search_format() + search
        yield from self.recursive_page_scraper(search_url)

    def recursive_page_scraper(self, url):
        soup = self._generate_soup(url)
        copysoup = soup

        for search_categories in self.check_categories(soup):
            print(search_categories)
            yield from self.recursive_page_scraper(search_categories)
        yield from self.scrape_prod_detail(soup)
        next_page = self.get_next_page(soup)
        if next_page != None:
            yield from self.recursive_page_scraper(next_page)


    def check_categories(self, soup):
        category_soup = soup.find_all(class_="clp-category")
        if category_soup is not None:
            for category in category_soup:
                yield category.find(class_="overlay-on-hover")['href']

        type_soup = soup.find_all(class_="lp-typeItem")
        if type_soup is not None:
            for type_item in type_soup:
                yield type_item.find(class_="overlay-on-hover")['href']


if __name__ == '__main__':
    test = ScrapeBHPhoto()

    for product in test.scrape_search('A10-7700K 3.4 GHz Quad-Core'):
        print(product)
