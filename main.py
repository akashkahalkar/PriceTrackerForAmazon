import requests #pip install requests
from bs4 import BeautifulSoup #pip install bs4
from notify_run import Notify #pip install notify_run
import time
import json

#getting config parameter from 'products.json' file
with open('products.json','r') as file:
    settings = json.load(file)
    file.close()

#get configuration parameters
items = settings['items'] #list of items
repeateTime = settings['repeat_after'] #ping time
notificationChanel = settings['notification_channel'] #notification channel
userAgetString = settings['user_agent'] #useragent string
#creating notification object with created notification channel.
notify = Notify(endpoint=notificationChanel)

if items is None:
    print("No product urls found.")
    exit(0)

# Google "My User Agent" And Replace It
headers = {"User-Agent": userAgetString} 
cookies = {}

def CheckPrice(url, price):
    try:
        page = requests.get(url, headers=headers, cookies=cookies)
    except requests.ConnectionError:
        print("🥵 Error occured!!! please check User agent string and Internet connectivity 🧐")
        exit(0)
    soup = BeautifulSoup(page.content, 'html.parser')
        #Finding the elements
    if soup.find(id= "productTitle") != None:
        product_title = soup.find(id= "productTitle").get_text().strip() #strip() to remove special characters
    else:
        return
    if  soup.find (id= "priceblock_ourprice") != None:
        product_price = soup.find (id= "priceblock_ourprice").get_text().strip()
    else:
        return
    
    #remove currency symbols
    productPriceString = ''.join(i for i in product_price if i.isdigit() or i == '.')

    #Converting the string to integer
    product_price = float(productPriceString)
    print("-----------------------------------------------")
    print("The Product Name is:" ,product_title)
    print("The Price is:" ,product_price)

    ##need logic to exit loop if all products have been checked
    # checking the price

    if price != 0 and product_price != float(price):
        percentage = percentageOfDifference(price, product_price)
        change = getDifference(percentage)
        notificationString = "[🤩]["+ str(product_price)+ "] Price for item: "+product_title[0:30]+ " "+ change+" by "+str(percentage)+"%"
        #update configuration file for updated changes
        updateConfigurationFile(items, settings, product_price, url)
        print(notificationString)
    else:
        #initial case when price was no set in configuration
        if price == 0:
            updateConfigurationFile(items, settings, product_price, url)
        notificationString = "[😴] 🎁: " + product_title[0:30] + ", 💰: " + str(product_price)
        print(notificationString)
    notify.send(notificationString)
   # handle the exception

def updateConfigurationFile(items, settings, updatedPrice, url):
      #write updated values to products
        for item in items:
            if item['url'] == url:
                item['budget'] = updatedPrice
        settings['items'] = items
        with open('products.json', 'w+') as outFile:
            json.dump(settings, outFile, indent=4)
            outFile.close()

def percentageOfDifference(original, changed):
    percentage = int(((changed - original)/original) * 100)
    return percentage

def getDifference(percentage):
    return "increased" if percentage > 0 else "decreased"

while True:
    for product in items:
        product_url = product['url']
        product_price = float(product['price'])
        CheckPrice(product_url, product_price)
    #set repeat time for script specified in seconds
    time.sleep(repeateTime)