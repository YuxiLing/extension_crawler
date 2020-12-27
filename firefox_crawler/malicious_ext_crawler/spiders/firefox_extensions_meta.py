import scrapy
import scrapy_selenium
from scrapy_selenium import SeleniumRequest
import pandas as pd
import re

import csv
import codecs
from datetime import datetime
import dateutil.parser as dparser


#Class for defining how your spider is gonna work~!
class FirefoxExtensionsMeta(scrapy.Spider):
    # Name of this spider
    name = 'firefox_extensions_meta'

    # PREPARATION for Start Requests
    # before parsing
    def start_requests(self):
        # List of urls for crawling
        urls = []
        # Path to keywords.csv
        path_keywords_csv = './malicious_ext_crawler/spiders/all_keywords.csv'
        # READ and GENERATE urls with keywords 
        with open(path_keywords_csv, mode='r', encoding='utf-8-sig') as csv_file:
            data = csv.reader(csv_file)
            for row_keyword in data:
                combined_keyword_url = 'https://addons.mozilla.org/en-US/firefox/search/?q=%s&type=extension' % row_keyword[0]
                urls.append(combined_keyword_url)
        # SEND and REQUEST the urls using selenium driver/chrome
        for url in urls:
            yield scrapy_selenium.SeleniumRequest(url=url, callback=self.parse)

    # PARSING the data from pages
    # @response :response from selenium requests
    def parse(self, response):
        # get full response
        extensions = response.css('.SearchResult')
        # get extension details
        for extension in extensions:
            # Extract metadata of each extensions
            
            name = extension.css('.SearchResult-link::text').get()
            text_user_numbers = extension.css('.SearchResult-users-text::text').get()
            # get user numbers 
            user_numbers = re.findall("[-+]?\d*\,?\d+|\d+", text_user_numbers)
            text_rating = extension.css('.visually-hidden::text').get()
            # text_rating  = extension.find_element_by_css_selector('.visually-hidden').text
            rating = re.findall("[-+]?\d*\.?\d+|\d+", text_rating)
            # equal to 0 if there is no valid rating
            if len(rating) == 0:
                rating = [0]

            creator = extension.css('h3.SearchResult-author.SearchResult--meta-section::text').get()
            
            details_link = extension.css('.SearchResult-link::attr(href)').get()
            # key_id of extension
            key = re.search('firefox/addon/(.+?)/', details_link).group(1)

            if details_link is not None:
                details_link = response.urljoin(details_link)
                # yield scrapy.Request(next_page, callback=self.parse)
                yield scrapy_selenium.SeleniumRequest(url=details_link, callback=self.parse_extension, cb_kwargs={'name':name,'user_numbers' :user_numbers[0], 'rating' :float(rating[0]), 'creator' :creator, 'key' :key})
        
        # NEXT PAGE and repeat parse method.
        next_page = response.css('a.Button.Button--cancel.Paginate-item.Paginate-item--next::attr("href")').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy_selenium.SeleniumRequest(url=next_page, callback=self.parse)

    # PARSING extensions
    # @parameters take parameters that are parsed data from previous request
    def parse_extension(self, response, name,user_numbers, rating, creator, key):
        last_updated = response.css('dd.Definition-dd.AddonMoreInfo-last-updated::text').get()
        # extracted_last_updated = re.search(r'\d{4} \d{2} \d{2})', last_updated)
        # formated_last_updated = datetime.strptime(match.group(), '%Y-%m-%d').date()
        shortened_last_updated = last_updated.split('(', 1)[1].split(')')[0]
        formated_last_updated = dparser.parse(shortened_last_updated,fuzzy=True)
        download_link=response.css('.InstallButtonWrapper-download-link::attr(href)').get()
        #example link: https://addons.mozilla.org/firefox/downloads/file/3692087/cuidaelrut-2.0.2-an+fx.xpi
        id=download_link.split('/')[6]
        
        reviews_list = [] # Store reviews list and void repeating in parse reviews
        # store previous parsed data as a dictionary
        previous_data = {
            
            "id": id,
            "download_link":download_link,
            "key": key,
            "name": name,
            "user_numbers": user_numbers,
            "rating": rating,
            "creator": creator,
            "last_updated": formated_last_updated,
            "reviews_list": reviews_list
        }

        
        
        # For extensions that dont have reviews (no reviews_links)
        yield {
            'platform': "firefox",
            "id": previous_data["id"],
            "download_link":previous_data["download_link"],
            'key': previous_data["key"],
            'name': previous_data["name"],
            'rating': previous_data["rating"],
            'user_numbers': previous_data["user_numbers"],
            'creator': previous_data["creator"],
            'last_updated': previous_data["last_updated"],
            'reviews': [] #as a empty list if there is no valid reviews
        }

        
        


        
