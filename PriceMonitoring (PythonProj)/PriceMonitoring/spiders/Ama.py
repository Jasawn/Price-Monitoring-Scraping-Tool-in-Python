from scrapy import Selector
from selenium import webdriver
import time
import re
import csv



web = webdriver.Chrome()
web.maximize_window()                                   #Initiate a browser
url = "https://www.lazada.sg/catalog/?spm=a2o42.home.search.1.654346b5WQ5TVU&q=acer%20laptop"                              #Parse URL into the browser
ShaB = web.get(url)                                         #Open the URL in the browser
time.sleep(2)

webheight = web.execute_script("return document.body.scrollHeight")  #the website have to scroll if not some data wont appear
for i in range(1, webheight, 5):
    web.execute_script("window.scrollTo(0, {});".format(i))
time.sleep(2)

responsehtml = web.page_source
response = Selector(text=responsehtml)

counter = 0
for product in response.xpath('//div[@class="_3VkVO"]'):
    name = product.xpath('//div[@class="_3VkVO"]/div/div/div/div[contains(@class,"_8JShU")]/a/@href').getall()
    #overlapname = product.xpath('//a[@class="tag_brn t_abv"]/text()').getall()
    #name = product.xpath('//div[@class="sbj"]/a[contains(@href, "item")]/text()').getall()
    #linkraw = product.xpath('//div[@class="sbj"]/a/@href').getall()
    #img = product.xpath('//td[@class="td_thmb"]/div/a/img/@src').getall()
    #price = product.xpath('//td[@class="td_prc"]/div/strong/text()').getall()
print(len(name))
print(name)
#for names in name:
#    for overlap in overlapname:
#        if overlapname != "":
#            if names == overlap:
#                name.remove(names)

#for link in linkraw:
#    if re.findall("gmkt.inc", link):
#        linkraw.remove(link)

QoData = {}

#for a in range(0, len(linkraw)):
#    QoData[a + 1] = linkraw[a], img[a],name[a],price[a],"Not Applicable"

#print(QoData)
#print(len(QoData))
#with open("Qo.csv", 'w', newline='', encoding='UTF8') as test:                   #Append data to CSV, but damn messy i will go update the code later hurhur
#    adddata = csv.writer(test)
#    adddata.writerow(["Product Link", "Image Link","Product Name", "Price", "Items Being Sold"])
#    for a in range(0, len(QoData)):
#        adddata.writerow(QoData[a+1])

#web.quit()