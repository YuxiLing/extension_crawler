import scrapy
import scrapy_selenium
from scrapy_selenium import SeleniumRequest
import pandas as pd
import re

import csv
import codecs
from datetime import datetime
import dateutil.parser as dparser
import calendar


# Class for defining how your spider is gonna work~!
class OperaExtensionsMeta(scrapy.Spider):
    # Name of this spider
    name = 'opera_extensions_meta'
    start_urls = ['https://addons.opera.com']
    headers = {
        "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 OPR/72.0.3815.378"

    }

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
                combined_keyword_url = 'https://addons.opera.com/en/search/?query=%s' % row_keyword[0]
                urls.append(combined_keyword_url)
        # SEND and REQUEST the urls using selenium driver/chrome
        for url in urls:
            yield scrapy_selenium.SeleniumRequest(url=url, callback=self.parse, headers=self.headers)

    # PARSING the data from pages
    # @response :response from selenium requests
    def parse(self, response):
        # get full response
        extensions = response.css('li.package.span-one-fourth.s-top-margin')
        # get extension details
        for extension in extensions:
            # Extract metadata of each extensions

            name = extension.css('h4.h-pkg-name::text').get()

            details_link = extension.css('a::attr(href)').get()
            # key_id of extension
            key = re.search('/en/extensions/details/(.+?)/',
                            details_link).group(1)

            if details_link is not None:
                details_link = response.urljoin(details_link)
                # yield scrapy.Request(next_page, callback=self.parse)
                yield scrapy_selenium.SeleniumRequest(url=details_link, callback=self.parse_extension, cb_kwargs={'name': name, 'key': key}, headers=self.headers)

        # NEXT PAGE and repeat parse method.
        next_page = response.css('a.hidden-text::attr("href")').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy_selenium.SeleniumRequest(url=next_page, callback=self.parse, headers=self.headers)

    # PARSING extensions
    # @parameters take parameters that are parsed data from previous request
    def parse_extension(self, response, name, key):

        # text_user_numbers = response.css('.h-byline.a::text').get()
        # get user numbers
        # user_numbers = re.findall("[-+]?\d*\,?\d+|\d+", text_user_numbers)
        rating = response.css('span#rating-value.rating::text').get()
        # equal to 0 if there is no valid rating
        if len(rating) == 0:
            rating = [0]

        creator_css = response.css('h2.h-byline')
        creator = creator_css.css('a::text').get()

        # last_updated = response.css('dd.Definition-dd.AddonMoreInfo-last-updated::text').get()
        # extracted_last_updated = re.search(r'\d{4} \d{2} \d{2})', last_updated)
        # formated_last_updated = datetime.strptime(match.group(), '%Y-%m-%d').date()
        # shortened_last_updated = last_updated.split('(', 1)[1].split(')')[0]
        # formated_last_updated = dparser.parse(shortened_last_updated,fuzzy=True)
        # meta_info=response.css('section.about.l-top-margin > dl > dd')
        # count=0
        download_numbers=-1
        formated_last_updated='0000-00-00'

        download_raw_numbers=response.css('section.about.l-top-margin > dl > dd:nth-child(2)::text').get()
        download_numbers = download_raw_numbers.replace(',','')

        last_updated=response.css('section.about.l-top-margin > dl > dd:nth-child(10)::text').get()
        date_list=re.split(r'[.;,\s]\s*',last_updated)
        # example data: July 30, 2019
        
        if date_list[0]=='Sept':
            month_num=9
        elif date_list[0]=='Aug':
            month_num=8
        elif date_list[0]=='July':
            month_num=7
        elif date_list[0]=='June':
            month_num=6
        elif date_list[0]=='April':
            month_num=4
        elif date_list[0]=='March':
            month_num=3
        else:
            month_num=list(calendar.month_abbr).index(date_list[0])
        formated_last_updated='%s-%s-%s' % (date_list[2],month_num,date_list[1])

        # for item in meta_info:
        #     count=count+1
        #     if count==1:
        #         download_numbers=item.css('dd::text').get()
        #     if count==10:
        #         last_updated=item.css('dd::text').get()
        #         date_list=re.split(r'[;,\s]\s*',last_updated)
        #         # example data: July 30, 2019
        #         month_num=list(calendar.month_abbr).index(date_list[0])
        #         formated_last_updated='%s-%s-%s' % (date_list[2],month_num,date_list[1])



        # download_url = response.css(
        #     'a.btn-install.btn-with-plus::attr(href)').get()
        download_link='https://addons.opera.com/extensions/download/'+key+'/'
        # download_link = download_url
        # example link: https://addons.opera.com/extensions/download/minter-link/
        # id=download_link.split('/')[5]

        # reviews_list = [] # Store reviews list and void repeating in parse reviews
        # store previous parsed data as a dictionary

        # For extensions that dont have reviews (no reviews_links)
        yield {
            'platform': "opera",
            "download_link": download_link,
            'key': key,
            'name': name,
            'rating': rating,
            'download_numbers': download_numbers,
            'creator': creator,
            'last_updated': formated_last_updated,
            'reviews': []  # as a empty list if there is no valid reviews
        }
