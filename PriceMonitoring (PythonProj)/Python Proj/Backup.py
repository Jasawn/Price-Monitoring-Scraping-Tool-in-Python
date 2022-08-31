from scrapy import Selector
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import pandas as pd
import json
import time
import re
import csv

def updatepricing(x):
    data = {}
    datalist = []

    url = x['Product Link'].values.tolist()
    data["Product Link"] = url

    for links in url:
        if re.search("shopee", links):
            datalist.append(updatepricingdataextraction(Create_browser(links), xpath(), 3))
        elif re.search("qoo10", links):
            datalist.append(updatepricingdataextraction(Create_browser(links), xpath(), 4))
        else:
            datalist.append(updatepricingdataextraction(Create_browser(links), xpath(), 5))

    data.update(updatepricingdatasort(datalist))

    appendtoexcel(data,3)

def updatepricingdataextraction(websource, pathdetails, pathnum):
    path = pathdetails[pathnum].keys()
    datalist = []

    for keys in path:
        details = websource.xpath(pathdetails[pathnum].get(keys)).get()
        if details == None:
            datalist.append("Not Available")
        else:
            datalist.append(details)
    return datalist

def updatepricingdatasort(data):
    Price = []
    Discounts = []
    Sorteddata = {}

    for items in data:
        if 'S' in items[0]:
            items[0] = items[0].replace("S", "")
        Price.append(items[0])
        Discounts.append(items[1])

    Sorteddata['Price'] = Price
    Sorteddata['Discounts'] = Discounts
    return Sorteddata

def Create_browser(link):
    web = webdriver.Chrome(options = webpagesize())
    web.get(link)
    time.sleep(2)
    response = retrievepagesource(web)
    return response

def scraping(x):
    shopeeweb = webdriver.Chrome(options = webpagesize())                                                      #run the browser in fullscreen
    qoweb = webdriver.Chrome(options = webpagesize())
    lazweb = webdriver.Chrome(options = webpagesize())


    ShaB = shopeeweb.get("https://shopee.sg/search?keyword=%s"%x)                                              #Open the URL in the browser
    Qo = qoweb.get("https://www.qoo10.sg/s/?keyword=%s&keyword_auto_change="%x)
    Laz = lazweb.get("https://www.lazada.sg/catalog/?spm=a2o42.home.search.1.654346b5WQ5TVU&q=%s"%x)


    scrolling(shopeeweb)
    scrolling(qoweb)
    scrolling(lazweb)

    lazpagesource = retrievepagesource(lazweb)

    rawshopeedata = dataextraction(retrievepagesource(shopeeweb),xpath(),0)
    rawqodata = dataextraction(retrievepagesource(qoweb),xpath(),1)
    rawlazdata = dataextraction(lazpagesource,xpath(),2)

    shopeedata = datasort(rawshopeedata,'Shopee')
    lazjsondata = lazjson(lazpagesource,rawlazdata)
    lazdata = datasort(lazjsondata, 'Lazada')
    qodata = datasort(rawqodata, 'Qoo10')

    appendtoexcel(shopeedata,0)
    appendtoexcel(qodata,1)
    appendtoexcel(lazdata,2)

    webquit(shopeeweb)
    webquit(qoweb)
    webquit(lazweb)

def webpagesize():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("window-size=1920,1080")
    return options

def scrolling(x):
    time.sleep(2)
    webheight = x.execute_script("return document.body.scrollHeight")                 #the website have to scroll if not some data wont appear
    for i in range(1, webheight, 70):
        x.execute_script("window.scrollTo(0, {});".format(i))

def retrievepagesource(x):
    responsehtml = x.page_source
    response = Selector(text=responsehtml)
    return response

def xpath():
    shopee = {'Product Details' : '//div[@class="col-xs-2-4 shopee-search-item-result__item"]',
    'Product Name' : ['//div[@class="_10Wbs- _5SSWfi UjjMrh"]/text()', '_10Wbs- _5SSWfi UjjMrh'],
    'Price' : ['//div[@class="zp9xm9 xSxKlK _1heB4J"]', 'zp9xm9 xSxKlK _1heB4J'],
    'Product Link' : ['//div[@class="col-xs-2-4 shopee-search-item-result__item"]/a/@href', 'col-xs-2-4 shopee-search-item-result__item'],
    'Product Image' : ['//div[@class="_25_r8I ggJllv"]/img/@src', '_25_r8I ggJllv'],
    'Items Sold' : ['//div[@class="_2VIlt8"]', '_2VIlt8']}

    qoo10 = {'Product Details' : '//div[@class="bd_lst_item"]/table/tbody/tr',
    'Product Name':['//div[@class="sbj"]/a[contains(@href, "item")]/text()', 'sbj'],
    'Price':['//td[@class="td_prc"]/div/strong/text()', 'td_prc'],
    'Product Link':['//div[@class="sbj"]/a[contains(@href, "item")]/@href', 'sbj'],
    'Product Image':['//td[@class="td_thmb"]/div/a/img/@src', 'td_thmb']}

    lazada = {'Product Details': '//div[@class="_3VkVO"]',
    'Product Name':['//div[@class="_3VkVO"]/div/div/div/div[contains(@class,"_8JShU")]/a/text()', '_3VkVO'],
    'Price':['//div[@class="_3VkVO"]/div/div/div/div[contains(@class,"LY2Vk")]/span/text()', '_3VkVO'],
    'Product Link':['//div[@class="_3VkVO"]/div/div/div/div[contains(@class,"_8JShU")]/a/@href', '_3VkVO']}

    shopeeupdateprice = {'Lowest Price' : '//div[@class="flex items-center _3iPGsU"]/div[contains(@class, "flex items-center")]/div[contains(@class,"Ybrg9j")]/text()',
    'Discounts' : '//div[@class="flex items-center _3iPGsU"]/div[contains(@class, "flex items-center")]/div[contains(@class,"_3LRxdy")]/text()'}

    qoo10updateprice = {'Lowest Price' : '//span[@id="discount_info"]/dl/dd/strong/text()',
    'Discounts' : '//span[@id="discount_info"]/dl/dd/span/text()'}

    lazadaupdateprice = {'Lowest Price' : '//span[@class=" pdp-price pdp-price_type_normal pdp-price_color_orange pdp-price_size_xl"]/text()',
    'Discounts' : '//span[@class="pdp-product-price__discount"]/text()'}

    return shopee,qoo10,lazada,shopeeupdateprice,qoo10updateprice,lazadaupdateprice

def dataextraction(websource,pathdetails,platform):
    counter = 0
    data = {}
    path = pathdetails[platform].keys()

    for keys in path:
        datalist = []
        if counter == 0:
            prodpath = pathdetails[platform].get(keys)
            numprod = len(websource.xpath(pathdetails[platform].get(keys)).getall())
            counter+=1
        else:
            classname = pathdetails[platform].get(keys)[1]
            b = 0
            for a in range(numprod):
                if re.search(classname, websource.xpath(prodpath)[a].get()):
                    datalist.append(websource.xpath(pathdetails[platform].get(keys)[0])[b].get())
                    b += 1
                else:
                    datalist.append('Not Available')
                    b = b
            data[keys] = datalist
    return data

def lazjson(websource,data):
    jsonscript = websource.xpath("//script[contains(text(), 'window.pageData')]/text()").get().replace("window.pageData = ", "").replace(";", "").strip()
    json_resp = json.loads(jsonscript)
    LazImage = {}
    LazImage['Product Image'] = [item.get("image") for item in json_resp.get("mods").get("listItems")]
    LazImage['Items Sold'] = [item.get("review") for item in json_resp.get("mods").get("listItems")]
    data.update(LazImage)
    return data

def datasort(data,platform):
    if platform == 'Shopee':
        length = len(data['Price'])
        linkdomain = 'https://shopee.sg'
        for a in range(length):
            searchprice = re.findall("(?<=>)(\d+)\D(\d+)\D", data['Price'][a])
            itemssold1 = re.findall("(?<=>)(\d+)", data['Items Sold'][a])

            if searchprice:
                if len(searchprice) == 2:
                    data['Price'][a] = data['Price'][a].replace(data['Price'][a],'$'+'.'.join(searchprice[0]) + ' - $' + '.'.join(searchprice[1]))
                else:
                    data['Price'][a] = data['Price'][a].replace(data['Price'][a],'$'+'.'.join(searchprice[0]))

            if itemssold1:
                data['Items Sold'][a] = data['Items Sold'][a].replace(data['Items Sold'][a],''.join(itemssold1) + ' sold')

            else:
                data['Items Sold'][a] = data['Items Sold'][a].replace(data['Items Sold'][a], "No Information")

            data['Product Link'][a] = linkdomain + data['Product Link'][a]
        return data

    elif platform == 'Lazada':
        length = len(data['Items Sold'])
        for a in range(length):
            if data['Items Sold'][a].isnumeric() == False:
                data['Items Sold'][a] = data['Items Sold'][a].replace(data['Items Sold'][a], "No Information")
            else:
                data['Items Sold'][a] = data['Items Sold'][a] + ' sold'
        return data

    elif platform == 'Qoo10':
        length = len(data['Price'])
        for a in range(length):
            if 'S' in data['Price'][a]:
                data['Price'][a] = data['Price'][a].replace("S", "")
        return data

def appendtoexcel(data,platform):
    timenow = datetime.now().strftime("%d%b%Y %H.%M.%S")
    dataframe = pd.DataFrame(data)
    if platform == 0:
        dataframe.to_csv("Results Shopee %s.csv"%timenow)
    elif platform == 1:
        dataframe.to_csv("Results Qoo10 %s.csv"%timenow)
    elif platform == 2:
        dataframe.to_csv("Results Lazada %s.csv"%timenow)
    elif platform == 3:
        dataframe.to_csv("Results from Update %s.csv"%timenow)

def webquit(web):
    web.quit()


userinput = scraping("Philips Hue")

#updatepricing(pd.read_csv("Selected-Master.csv"))
