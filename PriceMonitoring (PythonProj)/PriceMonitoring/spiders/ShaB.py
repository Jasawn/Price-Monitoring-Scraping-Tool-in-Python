from scrapy import Selector
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import csv
import time


userinput = ("philips hue")                             #Get input


options = Options()
options.add_argument("--headless")
options.add_argument("window-size=1920,1080")

url = "https://shopee.sg/search?keyword=asus%20laptop&page=1"                    #Parse URL into the browser
web = webdriver.Chrome(options = options)
ShaB = web.get(url)                                         #Open the URL in the browser
time.sleep(2)                                               #Let it run for 2s

webheight = web.execute_script("return document.body.scrollHeight")  #the website have to scroll if not some data wont appear
for i in range(1, webheight, 5):
    web.execute_script("window.scrollTo(0, {});".format(i))

responsehtml = web.page_source  #Get the inspect element
response = Selector(text=responsehtml)

for product in response.xpath('//div[@class="col-xs-2-4 shopee-search-item-result__item"]'):
    price = product.xpath('//div[@class="zp9xm9 xSxKlK _1heB4J"]').getall()
    linkraw = product.xpath('//div[@class="col-xs-2-4 shopee-search-item-result__item"]/a/@href').getall()
    imgsrc = product.xpath('//div[@class="_25_r8I ggJllv"]/img/@src').getall()
    name = product.xpath('//div[@class="_10Wbs- _5SSWfi UjjMrh"]/text()').getall()
    itemssoldinfo = product.xpath('//div[@class="_2VIlt8"]').getall()

price1 = []
itemssold = []

for a in range(0,len(price)):
    pricesplit = re.findall("(?<=>)(\d+)\D(\d+)\D", price[a])
    itemssold1 = re.findall("(?<=>)(\d+)", itemssoldinfo[a])

    if len(pricesplit) == 2:
        price1.append('$'+'.'.join(pricesplit[0]) + ' - $' + '.'.join(pricesplit[1]))

    else:
        price1.append('$'+'.'.join(pricesplit[0]))

    if itemssold1:
        itemssold.append(''.join(itemssold1))

    else:
        itemssold.append("No Information")

print(len(itemssoldinfo))
ShaBdata = {}
domain = 'https://shopee.sg'
for a in range(0, len(linkraw)):
    link = domain+linkraw[a]
    ShaBdata[a + 1] = link, imgsrc[a],name[a],price1[a],itemssold[a]

with open("shopee.csv", 'w', newline='', encoding='UTF8') as test:                   #Append data to CSV, but damn messy i will go update the code later hurhur
    adddata = csv.writer(test)
    adddata.writerow(["Product Link", "Image Link","Product Name", "Price", "Items Being Sold"])
    for a in range(0, len(ShaBdata)):
        adddata.writerow(ShaBdata[a+1])

web.quit()
print("Done!")
