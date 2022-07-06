import threading
import time

from bs4 import BeautifulSoup
from discord import Webhook, RequestsWebhookAdapter
from requests_html import HTMLSession

import config

#region --- VARIABLES ---
page_num = 0 # init to 0
interval = 10.05
init_time = next_execution = time.time()
session = HTMLSession()
colors = ['White', 'Black', 'Blue', 'Red', 'Green', 'Colorless']
logs_ch = Webhook.from_url("https://discord.com/api/webhooks/991149025359306842/xB000hauyghwVhEnotsO_oK-o7OVcFc4GMOe6EH5Rkhf4EJ9W4ZmCSKxn0pcHNYpniX4", adapter=RequestsWebhookAdapter())
cards_ch = Webhook.from_url("https://discord.com/api/webhooks/869137259981586433/P7m6kLCzReCr4RErUr1D-Ae-sqx6kta0igrnn5BdhCkzPfLWHiSRLyghrnc86-XLId_G", adapter=RequestsWebhookAdapter())
empty_page = False
#endregion

#region --- FUNCTIONS ---
def scrape_page():
    global page_num
    global next_execution
    global empty_page
    global colors
    
    if not empty_page: # increment page number if webpage success
        page_num += 1
    else: # change color if webpage error
        page_num = 1
        colors.append(colors[0])
        colors.pop(0)
        logs_ch.send(f'Now scraping {colors[0]}')
        print(f'now scraping {colors[0]}')
        empty_page = False

    url = f'https://www.tcgplayer.com/search/magic/product?RequiredFormat=All%20Formats&Price_Condition=Greater%20Than&Price=2&advancedSearch=true&productLineName=magic&view=list&Printing=Normal&page={page_num}&Condition=Near%20Mint%7CLightly%20Played&Language=English&ProductTypeName=Cards&RarityName=Mythic%7CRare&Color={colors[0]}' # update URL
    webpage = session.get(url); next_execution =  time.time() + interval # request webpage from url
    print(f'Requesting page {page_num} at ~{round(time.time() - init_time, 2)}s, response: {webpage.status_code}. URL: {url}')

    threading.Timer(max(0, next_execution - time.time()), scrape_page).start() # queue next scrape call

    webpage.html.render(sleep=3, timeout=15, retries=10) # render webpage
    soup = BeautifulSoup(webpage.html.raw_html, 'html.parser') # get soup

    cards = soup.findAll('div', class_='search-result')
    empty_page = False if cards else True
    print(f'Empty Page: {empty_page}')
    
    for data in cards: # call price check for each card
        price_check(data)

    print()

def price_check(data):
    name = data.find('span', class_='search-result__title')
    print(name.text)

    #region --- GET LISTINGS ---
    try:
        listings = data.findAll('section', class_='listing-item')
        listing_1 = listings[0]
        listing_2 = listings[1]
        listing_3 = listings[2]
    except:
        print("Not enough listings")
        print()
        return
    #endregion

    #region --- GET CARD PRICES ---
    price_1 = float(listing_1.find('div', class_='listing-item__price').text.replace(" ", "").replace("$", ""))
    price_2 = float(listing_2.find('div', class_='listing-item__price').text.replace(" ", "").replace("$", ""))
    price_3 = float(listing_3.find('div', class_='listing-item__price').text.replace(" ", "").replace("$", ""))
    #endregion

    #region --- GET SHIPPING COST --- 
    shipping_1 = get_shipping(listing_1)
    shipping_2 = get_shipping(listing_2)
    shipping_3 = get_shipping(listing_3)
    #endregion

    #region --- PRINT CARD INFO ---
    print(f'Listing 1: ${price_1}, ${shipping_1} Shipping')
    print(f'listing 2: ${price_2}, ${shipping_2} Shipping')
    print(f'listing 3: ${price_3}, ${shipping_3} Shipping')
    #endregion

    #region --- CALCULATE PROFIT ---
    
    cost_1 = round(sorted([price_1 + shipping_1, price_2 + shipping_2, price_3 + shipping_3])[0] * (1 + config.sales_tax / 100), 2)
    cost_2 = round(sorted([price_1 + shipping_1, price_2 + shipping_2, price_3 + shipping_3])[1] * (1 + config.sales_tax / 100), 2)
    differential = round(abs(sorted([price_1, price_2, price_3])[0] - sorted([price_1, price_2, price_3])[1]), 2)
    cost = min(cost_1, cost_2)
    revenue = max(cost_1, cost_2) - 0.01
    fees = (config.stamp_cost + config.letter_cost) if revenue < 20 else (config.bubble_mailer + config.shipping_label)
    revenue = round(revenue * (1 - (config.marketplace_comission + config.credit_card_precent_fee) / 100) - fees, 2)
    profit = round(revenue - cost, 2)
    margin = round(profit / revenue * 100, 2)
    print(f'cost: {cost}, revenue: {revenue}, profit: {profit}')
    print(f'margin: {margin}%')
    print()

    if margin > (config.target_margin):
        cards_ch.send(f'``` {name.text} | Cost: ${cost} | Profit: ${profit} | Margin: {margin}% | differential: {differential} | Popularity Ranking: {page_num - 1} ``` || https://www.tcgplayer.com{data.find(tabindex = "-1").get("href")} ||')
        pass

    #endregion

def get_shipping(listing):
    try:
        shipping = listing.find('div', class_='listing-item__info').find('span').text
    except:
        shipping = "0.00"
    
    if shipping.startswith("Free Shipping on Orders Over"):
        shipping = 2.49
    else:
        shipping = shipping.replace("+", "").replace("$", "").replace(" ", "").replace("Shipping", "")
    
    return float(shipping)

#endregion

#region --- MAIN ---
logs_ch.send(f"**Bot online: {time.ctime()}**")
cards_ch.send(f'```fix\n{time.ctime()}```')

try:
    scrape_page()
except:
    logs_ch.send(f"**Bot offline: {time.ctime()}**")

#endregion

#region --- TODO ---

# on startup scrape every set on tcgp and remove the whitelist
# have all sets in a whitelist, and then a list called blacklisted sets
# remove all blacklisted sets from whitelist, then include all whitelisted sets in url 

# "Free shipping on orders over $50" makes your shiping appear as $0 when sorting cards by price
# however, the shipping in reality costs fucking $2.49 lol

#endregion
