from scrapy import Selector
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime
import pandas as pd
import json
import time
import re

options = Options()
options.add_argument("start-maximized")
options.add_argument("--headless")
web = webdriver.Chrome()
time.sleep(2)
web.get('https://www.lazada.sg/products/acer-aspire-1-a115-32-c33asilver-156-inch-fhd-display-with-preloaded-microsoft-office-365-personal-i1102780293-s10148640167.html?search=1&freeshipping=1')
time.sleep(3)
web.refresh()
responsehtml = web.page_source
response = Selector(text=responsehtml)

price = response.xpath('//span[@class=" pdp-price pdp-price_type_normal pdp-price_color_orange pdp-price_size_xl"]/text()').get()
print(price)




#print(responsehtml)

#time.sleep(5)
#move = ActionChains(web)
#try:
#    container = web.find_element_by_id("nc_1__scale_textee")
#    slider = web.find_element_by_id('nc_1_n1z')
#except NoSuchElementException:
#    print('no')

#move.click_and_hold(slider).move_by_offset(container.size['width'], 0).release().perform()
