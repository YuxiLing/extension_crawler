


import scrapy
import scrapy_selenium
from scrapy_selenium import SeleniumRequest
import pandas as pd
import re

import csv
import codecs

class FirefoxDetailsCreator(scrapy.Spider):
    # Name of this spider
    name = 'firefox_details_creator'


    # PREPARATION for Start Requests
    # before parsing
    def start_requests(self):
        # List of urls for crawling
        urls = []
        # Path to selected_extensions.csv
        path_keywords_csv = 'malicious_ext_crawler/spiders/selected_extensions.csv'
        # READ and GENERATE urls with keywords 
        with open(path_keywords_csv, mode='r', encoding='utf-8-sig') as csv_file:
            data = csv.reader(csv_file)
            for row_keyword in data:
                combined_keyword_url = 'https://addons.mozilla.org/en-US/firefox/addon/%s/?src=search' % row_keyword[0]
                urls.append(combined_keyword_url)
        # SEND and REQUEST the urls using selenium driver/chrome
        for url in urls:
            yield scrapy_selenium.SeleniumRequest(url=url, callback=self.parse_extension)

     # PARSING extensions
    # @parameters take parameters that are parsed data from previous request
    def parse_extension(self, response):
    

        # Retrieve creator profile
        creator = []

        # store previous parsed data as a dictionary
        previous_data = {
            # "key": key,
            "name": response.css('h1.AddonTitle::text').get(),
            "creator_details": creator
        }

        

       
        creator_link = response.css('span.AddonTitle-author a::attr("href")').get()
        if creator_link is not None:
            creator_link = response.urljoin(creator_link)
            yield  scrapy_selenium.SeleniumRequest(url=creator_link, callback = self.parse_creator, cb_kwargs={'previous_data':previous_data})
        else:
            yield {
            # 'platform': "firefox",
            # 'key': previous_data["key"],
                'name': previous_data["name"],
                'creator_details': []
            }


    def parse_creator(self, response, previous_data):
        name = response.css("h1.UserProfile-name::text").get()
        location = response.css("dd.Definition-dd.UserProfile-location::text").get()
        user_since = response.css("dd.Definition-dd.UserProfile-user-since::text").get()
        num_of_addons = response.css("dd.Definition-dd.UserProfile-number-of-addons::text").get()

        creator_item = {
            'name': name,
            'location': location,
            'user_since': user_since,
            'num_of_addons': num_of_addons
        }

        previous_data["creator_details"].append(creator_item)

        yield {
            'name': previous_data["name"],
            'creator_details': previous_data["creator_details"]
        }