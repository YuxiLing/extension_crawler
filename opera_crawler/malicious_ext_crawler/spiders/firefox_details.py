import scrapy
import scrapy_selenium
from scrapy_selenium import SeleniumRequest
import pandas as pd
import re

import csv
import codecs

class FirefoxDetails(scrapy.Spider):
    # Name of this spider
    name = 'firefox_details'


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
        last_updated = response.css('dd.Definition-dd.AddonMoreInfo-last-updated::text').get()
        reviews_list = [] # Store reviews list and void repeating in parse reviews

        # Rating 
        text_rating = response.css('div.AddonMeta-rating-title::text').get()
        rating = re.findall("[-+]?\d*\.?\d+|\d+", text_rating)

        # Retrieve creator profile
        # creator_link = response.css('span.AddonTitle-author a::attr("href")').get()
        # if creator_link is not None:
        #     creator_link = response.urljoin(creator_link)
        #     yield  scrapy_selenium.SeleniumRequest(url=creator_link, callback = self.parse_creator)

        # store previous parsed data as a dictionary
        previous_data = {
            # "key": key,
            "name": response.css('h1.AddonTitle::text').get(),
            "user_numbers": response.css('dd.MetadataCard-content::text').get(),
            "rating": rating,
            # "creator": self.creator,
            "detail_creator": response.css('span.AddonTitle-author a::attr("href")').get(),
            "last_updated": last_updated,
            "reviews_list": reviews_list
        }

        

        # PS: Not every extension has reviews
        reviews_link = response.css('a.AddonMeta-reviews-title-link::attr("href")').get()
        if reviews_link is not None:
            reviews_link = response.urljoin(reviews_link)
            yield  scrapy_selenium.SeleniumRequest(url=reviews_link, callback = self.parse_reviews, cb_kwargs={'previous_data':previous_data})
        
        else:
            # For extensions that dont have reviews (no reviews_links)
            yield {
            # 'platform': "firefox",
            # 'key': previous_data["key"],
            'name': previous_data["name"],
            'rating': previous_data["rating"],
            'user_numbers': previous_data["user_numbers"],
            # 'creator': previous_data["creator"],
            'last_updated': previous_data["last_updated"],
            'reviews': [] #as a empty list if there is no valid reviews
        }

    # PARSING reviews from a extension
    # @parameters take previous parsed data as an argument
    def parse_reviews(self, response, previous_data):
        reviews = response.css('li')
        # stupid bug s and without s
        for review in reviews:
            # content = review.css('div::text').get()
            temp_css_content_with_br = review.css('div.ShowMoreCard-contents')
            # <br> HANDLER including parsing reviews and eliminating <br>
            content = temp_css_content_with_br.xpath('string(.)').get()
            # content = review.xpath('//*[@id="react-view"]/div/div/div/div[2]/div/section/div/ul/li[1]/div/div/div/section/div/div/div::text').get()
            if content is not None:
                previous_data["reviews_list"].append(content)

        # NEXT PAGE and repeat parse method.
        next_page_reviews = response.css('a.Button.Button--cancel.Paginate-item.Paginate-item--next::attr("href")').get()
        if next_page_reviews is not None:
            next_page_reviews = response.urljoin(next_page_reviews)
            yield scrapy_selenium.SeleniumRequest(url=next_page_reviews, callback=self.parse_reviews, cb_kwargs={'previous_data':previous_data})
        else:
            # Avoid repeating when do paging parse why???? maybe after selenium request and callback, it creates two processes, one for call def parse_reviews ,one for continuing 
            # processing the next piece of code.
            # Export data with reviews list
            yield {
                # 'platform': "firefox",
                # 'key': previous_data["key"],
                'name': previous_data["name"],
                'rating': previous_data["rating"],
                'user_numbers': previous_data["user_numbers"],
                # 'creator': previous_data["creator"],
                'last_updated': previous_data["last_updated"],
                'reviews': previous_data["reviews_list"] #as a empty list if there is no valid reviews
            }

    


        
