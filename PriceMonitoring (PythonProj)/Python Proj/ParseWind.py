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
import random

def updatepricing(x):
    ### Second part of the program, extracting the price of each specific product in order to monitor price
    ### Will be using the Product link from the user choose, and extract the price from it specifically

    data = {}
    datalist = []

    ### Extract the URL from excel and convert the dataframe to list
    url = x['Product Link'].values.tolist()
    data["Product Link"] = url

    for links in url:
        ### Check which platform each URL is, different websites uses different Xpath to extract data
        ### createbrowser will open a browser and url will be parse to the browser and retrieve page source
        if re.search("shopee", links):
            datalist.append(updatepricingdataextraction(createbrowser(links,0), xpath(), 3))
        elif re.search("qoo10", links):
            datalist.append(updatepricingdataextraction(createbrowser(links,1), xpath(), 4))
        elif re.search("lazada", links):
            datalist.append(updatepricingdataextraction(createbrowser(links,2), xpath(), 5))

    data.update(updatepricingdatasort(datalist)) #Data clean up

    appendtoexcel(data,3) #Append the sorted data to excel

def updatepricingdataextraction(websource, pathdetails, pathnum):
    ### Using the page source to extract the price

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
    price = []
    discounts = []
    sorteddata = {}

    for items in data:
        if 'S' in items[0]:
            items[0] = items[0].replace("S", "")
        price.append(items[0])
        discounts.append(items[1])

    sorteddata['Price'] = price
    sorteddata['Discounts'] = discounts
    return sorteddata

def createbrowser(link,platform):
    ### Lazada website have bot detection system implemented meanwhile the other platforms doesnt have
    ### If platform is not Lazada, then it will run as per normal

    if platform == 0 or platform == 1:
        web = webdriver.Chrome(options = webpagesize())
        web.get(link)
        time.sleep(random.randint(2,5))
        response = retrievepagesource(web)
        return response
    else:
        ### If we are opening a lazada website
        web = webdriver.Chrome(options = webpagesize())
        web.maximize_window()
        time.sleep(random.randint(2,5))
        web.get(link)

        ### Making the pause time as random as possible to avoid detection
        time.sleep(random.randint(2,5))
        web.refresh() #Refresh the page in order to try to access the website.
        try:
            ### This is to find if there is slider captcha needed to be done
            container = web.find_element_by_id("nc_1__scale_text") #Find the container
            slider = web.find_element_by_id('nc_1_n1z') #The button required to press and slide in the container
            move = ActionChains(web)
            move.click_and_hold(slider).move_by_offset(container.size['width'], 0).release().perform() #The function to simulate human's sliding
            response = retrievepagesource(web)
            return response
        except NoSuchElementException:
            ### If there is no captcha after refreshing, the website will run as per normal
            response = retrievepagesource(web)
            return response

def scraping(x):
    ### Open 3 browers for 3different websites
    shopeeweb = webdriver.Chrome(options = webpagesize())
    qoweb = webdriver.Chrome(options = webpagesize())
    lazweb = webdriver.Chrome(options = webpagesize())

    ### Parse the URL into the browser opened (%x means userinput)
    ShaB = shopeeweb.get("https://shopee.sg/search?keyword=%s"%x)
    Qo = qoweb.get("https://www.qoo10.sg/s/?keyword=%s&keyword_auto_change="%x)
    Laz = lazweb.get("https://www.lazada.sg/catalog/?spm=a2o42.home.search.1.654346b5WQ5TVU&q=%s"%x)

    ### All 3 websites requires simulate scrolling to the bottom in order to run the JS (done so using a function)
    scrolling(shopeeweb)
    scrolling(qoweb)
    scrolling(lazweb)

    lazpagesource = retrievepagesource(lazweb) #Separate page source to retrieve Image and Items review from JSON

    ### Parse JS loaded page source using retrievepagesource function, retrieve Shopee Xpath that is stored in as a dictionary.. Using xpath to extract data from PageSource
    ### The numbers behind xpath() is to indicate to dictionary position
    rawshopeedata = dataextraction(retrievepagesource(shopeeweb),xpath(),0)
    rawqodata = dataextraction(retrievepagesource(qoweb),xpath(),1)
    rawlazdata = dataextraction(lazpagesource,xpath(),2)

    ### Parse the unsorted data retrieved above and proceed with sorting accordingly based on websites
    shopeedata = datasort(rawshopeedata,'Shopee')
    lazjsondata = lazjson(lazpagesource,rawlazdata) #Pass the dictionary from rawlazdata and update the dict with Images / Itemssold from JSON side
    lazdata = datasort(lazjsondata, 'Lazada')
    qodata = datasort(rawqodata, 'Qoo10')

    ### Parse sorted data and append it to excel
    appendtoexcel(shopeedata,0)
    appendtoexcel(qodata,1)
    appendtoexcel(lazdata,2)

    ### Close the browser that was initiated above
    webquit(shopeeweb)
    webquit(qoweb)
    webquit(lazweb)

def webpagesize():
    ### Running the browser in the background and fullscreen
    options = Options()
    options.add_argument("--headless") #Run the browser in background
    options.add_argument("window-size=1920,1080") #Full-screen
    return options

def scrolling(x):
    ### Make sure the website is loaded before scrolling of the webpage to load the JS (Certain data will not appear without running the JS)
    time.sleep(random.randint(2,4))
    webheight = x.execute_script("return document.body.scrollHeight") #Retrieve the height of the webpage
    for i in range(1, webheight, 70): #Scroll the webpage to the bottom at a interval of 70
        x.execute_script("window.scrollTo(0, {});".format(i)) #Cannot scroll too fast as some data will get missed out

def retrievepagesource(x):
    responsehtml = x.page_source  #Retrieve the HTML of the page after JS have loaded
    response = Selector(text=responsehtml) #Parse the HTML as selector in order to use xpath .get() afterwards
    return response

def xpath():
    ### Xpath declared for each item according to each websites

    shopee = {'Product Details' : '//div[@class="col-xs-2-4 shopee-search-item-result__item"]',
    'Product Name' : ['//div[@class="_10Wbs- _5SSWfi UjjMrh"]/text()', '_10Wbs- _5SSWfi UjjMrh'],
    'Price' : ['//div[@class="zp9xm9 xSxKlK _1heB4J"]', 'zp9xm9 xSxKlK _1heB4J'],
    'Product Link' : ['//div[@class="col-xs-2-4 shopee-search-item-result__item"]/a/@href', 'col-xs-2-4 shopee-search-item-result__item'],
    'Product Image' : ['//div[@class="_25_r8I ggJllv"]/img/@src', '_25_r8I ggJllv'],
    'Items Sold' : ['//div[@class="_2VIlt8"]', '_2VIlt8']}

    qoo10 = {'Product Details' : '//div[@class="bd_lst_item"]/table/tbody/tr',
    'Product Name':['//div[@class="sbj"]/a[contains(@href, "item")]/text()', 'sbj'], #There are 2 links under this classname, url containing "item" is the one we want
    'Price':['//td[@class="td_prc"]/div/strong/text()', 'td_prc'],
    'Product Link':['//div[@class="sbj"]/a[contains(@href, "item")]/@href', 'sbj'],
    'Product Image':['//td[@class="td_thmb"]/div/a/img/@src', 'td_thmb']}

    lazada = {'Product Details': '//div[@class="_3VkVO"]',
    'Product Name':['//div[@class="_3VkVO"]/div/div/div/div[contains(@class,"_8JShU")]/a/text()', '_3VkVO'], #Using contain[@class] allows us to pinpoint the data we wants
    'Price':['//div[@class="_3VkVO"]/div/div/div/div[contains(@class,"LY2Vk")]/span/text()', '_3VkVO'],
    'Product Link':['//div[@class="_3VkVO"]/div/div/div/div[contains(@class,"_8JShU")]/a/@href', '_3VkVO']}

    shopeeupdateprice = {'Lowest Price' : '//div[@class="flex items-center _3iPGsU"]/div[contains(@class, "flex items-center")]/div[contains(@class,"Ybrg9j")]/text()',
    'Discounts' : '//div[@class="flex items-center _3iPGsU"]/div[contains(@class, "flex items-center")]/div[contains(@class,"_3LRxdy")]/text()'}

    qoo10updateprice = {'Lowest Price' : '//strong[@id="qprice_span"]/text()',
    'Discounts' : '//span[@id="discount_info"]/dl/dd/span/text()'}

    lazadaupdateprice = {'Lowest Price' : '//span[@class=" pdp-price pdp-price_type_normal pdp-price_color_orange pdp-price_size_xl"]/text()',
    'Discounts' : '//span[@class="pdp-product-price__discount"]/text()'}

    return shopee,qoo10,lazada,shopeeupdateprice,qoo10updateprice,lazadaupdateprice

def dataextraction(websource,pathdetails,platform):
    ### This function is to make use of the pagesource(Loaded by JS) retrieve by selenium and extract data accordingly
    ### This function is constructed to be dynamic, no matter how many items a webpage can consists, it will still extract accordingly with XPath being specified

    counter = 0
    data = {}  # results will be stored in dictionary
    path = pathdetails[platform].keys()

    for keys in path:
        datalist = []
        if counter == 0:
            ### No data required to extract so skipping after getting the number of product and the xpath.

            prodpath = pathdetails[platform].get(keys) #Xpath of Product Details
            numprod = len(websource.xpath(pathdetails[platform].get(keys)).getall()) #Get the number of product present
            counter+=1
        else:
            ### Extraction of required data

            classname = pathdetails[platform].get(keys)[1] #Retrieving the classname for checking
            b = 0
            for a in range(numprod): #Loop accordingly to the number of products present on the webpage
                ### There are instances when the data we want does not exist and therefore classname(to retrieve the specific data) will not be present too
                ### So we check if classname exists in each product

                if re.search(classname, websource.xpath(prodpath)[a].get()):        #if classname dont exist in the product, append "not available" else append the data required into a list
                    datalist.append(websource.xpath(pathdetails[platform].get(keys)[0])[b].get())
                    b += 1
                else:
                    datalist.append('Not Available')
                    b = b
            data[keys] = datalist           #Add multiple values of the list to the dictionary
    return data

def lazjson(websource,data):
    ### In this function, the page source and the data scraped from previous function will be parse here
    ### The information (Image and item sold) is in one of the Script found in page source
    ### Image are unable to be scraped by using of XPath because it will disappear once the browser scrolls away
    ### Noticed that all the images are actually preloaded in on of the Script
    ### jsonscript cleans up the json so that extraction of data will be easier
    ### The data extracted from json will be added into a dictionary called LazImage
    ### After that it will merge the data scraped from previous function with LazImage and return the full dataset

    jsonscript = websource.xpath("//script[contains(text(), 'window.pageData')]/text()").get().replace("window.pageData = ", "").replace(";", "").strip()
    json_resp = json.loads(jsonscript)
    LazImage = {}
    LazImage['Product Image'] = [item.get("image") for item in json_resp.get("mods").get("listItems")]      #Extraction of data
    LazImage['Items Sold'] = [item.get("review") for item in json_resp.get("mods").get("listItems")]
    data.update(LazImage)       #Populate the original dictionary with new details
    return data

def datasort(data,platform):
    ### Unsorted data will be parse here and as well as the platform details because different platform's data requires different type of cleaning

    if platform == 'Shopee':
        length = len(data['Price'])
        linkdomain = 'https://shopee.sg'

        for a in range(length):
            ### The Price / Price range is mixed together with messy HTML tags, regex is used to sort them out
            ### 'Items sold' is mixed with messy HTML tags as well, there are instances when there is no value, No information will be added instead to be clear
            ### Product Link does not have domain, we added the domain into the data extracted
            ### Cleaned data will be updated back to dictionary again

            searchprice = re.findall("(?<=>)(\d+)\D(\d+)\D", data['Price'][a])      #Find the doubles in messy string
            itemssold1 = re.findall("(?<=>)(\d+)", data['Items Sold'][a])           #Find the int in messy string

            if searchprice:
                if len(searchprice) == 2:   #Shopee have 2values which is the range, then have to join the 2 numbers together as 1 and update the dictionary
                    ### Check if the price is in thousands or hundred, if thousands, the data will be joined by ',' else joined by '.'
                    if len(searchprice[0][1]) == 2:
                        lowerprice = '$'+'.'.join(searchprice[0])
                    else:
                        lowerprice = '$'+','.join(searchprice[0])
                    if len(searchprice[1][1]) == 2:
                        higherprice = '$'+'.'.join(searchprice[1])
                    else:
                        higherprice = '$'+','.join(searchprice[1])
                    data['Price'][a] = data['Price'][a].replace(data['Price'][a], lowerprice + ' - ' + higherprice)

                else:
                    if len(searchprice[0][1]) == 2:
                        price = '$'+'.'.join(searchprice[0])
                    else:
                        price = '$'+','.join(searchprice[0])
                    data['Price'][a] = data['Price'][a].replace(data['Price'][a], price)

            if itemssold1:  #Itemssold sold can be no value, if no value then add "No information" and update the dictionary
                data['Items Sold'][a] = data['Items Sold'][a].replace(data['Items Sold'][a],''.join(itemssold1) + ' sold')

            else:
                data['Items Sold'][a] = data['Items Sold'][a].replace(data['Items Sold'][a], "No Information")

            data['Product Link'][a] = linkdomain + data['Product Link'][a]
        return data

    elif platform == 'Lazada':
        ### For Lazada, some of the data extracted is empty. In order to be clearer, No information will replace empty dataset
        ### The Product link is invalid due to // infront of the URL, therefore it has to be removed in order for the link to work

        length = len(data['Items Sold'])
        for a in range(length):
            if data['Items Sold'][a].isnumeric() == False: #Check if theres number in the data extracted
                data['Items Sold'][a] = data['Items Sold'][a].replace(data['Items Sold'][a], "No Information")
            else:
                data['Items Sold'][a] = data['Items Sold'][a] + ' sold'

            data['Product Link'][a] = "https:" + data['Product Link'][a]
        return data

    elif platform == 'Qoo10':
        ### For Qoo10, the price consists of S infront of the value, in order to be organised, we remove S from the data

        length = len(data['Price'])
        for a in range(length):
            if 'S' in data['Price'][a]:
                data['Price'][a] = data['Price'][a].replace("S", "")
        return data

def appendtoexcel(data,platform):
    ### There can be multiple files being created to prevent confusion, datetime is added to naming convention for easier keep track

    timenow = datetime.now().strftime("%d%b%Y %H.%M.%S")
    dataframe = pd.DataFrame(data) #Using pandas dataframe to append the data into excel
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


#userinput = scraping("Laptop") #allow user input

updatepricing(pd.read_csv("Selected-Master.csv")) #For update of pricing
