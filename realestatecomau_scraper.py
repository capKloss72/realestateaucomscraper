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

    def get_property_details(self, page_listings_details_urls) -> list:
        feature_dict = OrderedDict()
        feature_list = []
        for property in page_listings_details_urls:
            house_request = requests.get(property)
            house_content = house_request.content
            house_soup = BeautifulSoup(house_content, "html.parser")
            house_info = house_soup.find_all("div", {"id": "primaryContent"})
            feature_dict['Street'] = house_soup.find("span", {"class": "street-address"}).text
            feature_dict['Locality'] = house_soup.find("span", {"itemprop": "addressLocality"}).text
            feature_dict['Region'] = house_soup.find("span", {"itemprop": "addressRegion"}).text
            feature_dict['Post Code'] = house_soup.find("span", {"itemprop": "postalCode"}).text
            for features in house_info:
                for feature in features.find_all("div", {"class": "featureList"}):
                    for line in feature.find_all("li"):
                        try:
                            heading = line.text
                            lst = re.findall('[^:]+', heading)
                            if len(lst) > 1:
                                feature_dict[lst[0]] = lst[1]
                        except AttributeError:
                            pass
            feature_list.append(feature_dict)
        return feature_list
