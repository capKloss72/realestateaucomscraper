import requests
from bs4 import BeautifulSoup
from collections import OrderedDict
import re


class RealEstateComScraper(object):

    def __init__(self, search_url, output_cvs="listings.csv", domain_url="https://www.realestate.com.au"):
        self.search_url = search_url
        self.output_cvs = output_cvs
        self.domain_url = domain_url

    def get_page_listings(self, page_url):
        """
        Returns a Result set containing all listings on the page
        :rtype: bs4.element.ResultSet
        """
        r = requests.get(page_url)
        c = r.content
        soup = BeautifulSoup(c, "html.parser")
        return soup.find_all("div", {"class": "listingInfo rui-clearfix"})

    def get_page_listings_details_urls(self, page_listings) -> list:
        page_listings_details_urls = []
        for listing in page_listings:
            details_url = self.domain_url + listing.find("h2", {"class": "rui-truncate"}).find('a')['href']
            page_listings_details_urls.append(details_url)
        return page_listings_details_urls

    def get_property_details(self, page_listings_details_urls) -> OrderedDict:
        feature_list = OrderedDict()
        for property in page_listings_details_urls:
            house_request = requests.get(property)
            house_content = house_request.content
            house_soup = BeautifulSoup(house_content, "html.parser")
            house_info = house_soup.find_all("div", {"id": "primaryContent"})
            for features in house_info:
                for feature in features.find_all("div", {"class": "featureList"}):
                    for line in feature.find_all("li"):
                        try:
                            heading = line.text
                            lst = re.findall('[^:]+', heading)
                            if len(lst) > 1:
                                feature_list[lst[0]] = lst[1]
                        except AttributeError:
                            pass
        return feature_list
