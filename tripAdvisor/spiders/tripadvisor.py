# -*- coding: utf-8 -*-
import scrapy
import time
from selenium import webdriver


class TripadvisorSpider(scrapy.Spider):
    name = 'tripadvisor'
    start_urls = ['https://www.tripadvisor.co.uk/Attractions-g186338-Activities-c20-t109-London_England.html/']

    def parse(self, response):
        links = response.css('div.listing_title a::attr(href)').extract() #list all links
        links = links[0:5] #set limit to 5 links
        for page in links: #for all links
            yield response.follow(page, self.parse_place) #follow the links and go to parse_place function


    def parse_place(self, response):
        def extract_with_css(query): #extract the data
            time.sleep(1) #add a 1 second delay
            return response.css(query).extract_first()

        def extract_with_xpath(query): #extract the data
            time.sleep(1) #add a 1 second delay
            return response.xpath(query).extract_first()

        def extract_city_postcode(query, isCity):
            time.sleep(1) #add a 1 second delay
            cityPostcodeString = response.xpath(query).extract() #get city and postcode together
            cityPostcodeString = str(cityPostcodeString) #convert to string
            cityPostcodeString = cityPostcodeString.split(' ') # split at each space
            if(isCity == True):
                city = cityPostcodeString[0] #pick the first word
                return city[2:] #cut the first two characters "['"
            else:
                return cityPostcodeString[1] + ' ' + cityPostcodeString[2] # ad the first and second part of postcode together

        ##function open the url in a browser and gets the url from the browser window
        def extractUrl():
            driver = webdriver.Chrome(r'C:\Users\ogran\SynologyDrive\My Documents\development\Scrapy\chromedriver.exe') #location of chromium driver
                # Optional argument, if not specified will search path.
            driver.get('https://www.tripadvisor.co.uk/Attraction_Review-g186338-d10847106-Reviews-Camden_Assembly-London_England.html'); #url to get
            time.sleep(4) # Let the user actually see something!

            try:
                click = driver.find_element_by_xpath('//*[@id="taplc_location_detail_header_attractions_0"]/div[2]/div/div[3]/span[2]') #try find the website url at the top of page
                click.click()
            except:
                print("blocked - trying lower url")
                click = driver.find_element_by_xpath('//*[@id="taplc_location_detail_contact_card_ar_responsive_0"]/div[3]/div[2]/div[1]/div/span[2]') #if the top of website is hidden try further down the page
                click.click()

            time.sleep(2)
            driver.switch_to_window(driver.window_handles[-1]) # switch windows
            url = driver.current_url # get the url

            driver.quit() #close the window
            return url


        yield { #results to get and run under extract funtion
            'Name': extract_with_xpath('//*[@id="HEADING"]/text()'),
            'Address': extract_with_xpath('//*[@id="taplc_location_detail_header_attractions_0"]/div[2]/div/div[1]/span[2]/text()'),
            'City': extract_city_postcode('//*[@id="taplc_location_detail_header_attractions_0"]/div[2]/div/div[1]/span[3]/text()', True),
            'Post Code': extract_city_postcode('//*[@id="taplc_location_detail_header_attractions_0"]/div[2]/div/div[1]/span[3]/text()', False),
            'Phone number': extract_with_xpath('//*[@id="taplc_location_detail_header_attractions_0"]/div[2]/div/div[2]/span[2]/text()'),
            'Website url': extractUrl(),
        }
