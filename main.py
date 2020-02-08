import requests #pip install requests
from bs4 import BeautifulSoup #pip install bs4
from notify_run import Notify #pip install notify_run
import time
import json

with open('products.json','r') as file:
    settings = json.load(file)
    file.close()

#get configuration parameters
items = settings['items']
repeateTime = settings['repeat_after']
notificationChanel = settings['notification_channel']
userAgetString = settings['userAgent']

if items is None:
    print("No product urls found.")
    exit

#to get notification, open given link and click on subscribe
notify = Notify(endpoint=notificationChanel)

# Google "My User Agent" And Replace It
headers = {"User-Agent": userAgetString} 
cookies = {}

def CheckPrice(url, price):
    try:
        page = requests.get(url, headers=headers, cookies=cookies)
    except requests.ConnectionError as e:
        print(e)
        exit 
   # handle the exception
    
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
    if(product_price != float(price)):
        changeType = ""
        if product_price > price:
            changeType = " increased"
        else:
            changeType = " decreased"
        notificationString = "🥶 item: " + product_title[0:20] + changeType +" to: " + str(product_price)
        
        #update configuration file for updated changes
        updateConfigurationFile(items, settings, product_price, url)
        print(notificationString)
        notify.send(notificationString)
    else:
        notificationString = "😴 item: " + product_title[0:20] + ": " + str(product_price)
        print(notificationString)
        notify.send(notificationString)

def updateConfigurationFile(items, settings, updatedPrice, url):
      #write updated values to products
        for item in items:
            if item['url'] == url:
                item['budget'] = updatedPrice
        settings['items'] = items
        with open('products.json', 'w+') as outFile:
            json.dump(settings, outFile, indent=4)
            outFile.close()


while True:
    for product in items:
        product_url = product['url']
        product_price = product['budget']
        CheckPrice(product_url, product_price)
    #set repeat time for script specified in seconds
    time.sleep(repeateTime)