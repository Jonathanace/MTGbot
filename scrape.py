import threading
import time
from bs4 import BeautifulSoup
from requests_html import HTMLSession
from discord import Webhook, RequestsWebhookAdapter
import requests

start_time = time.time()
webhook = Webhook.from_url("https://discord.com/api/webhooks/869137259981586433/P7m6kLCzReCr4RErUr1D-Ae-sqx6kta0igrnn5BdhCkzPfLWHiSRLyghrnc86-XLId_G", adapter=RequestsWebhookAdapter())
html_text = requests.get('https://www.tcgplayer.com/search/all/product?q=goblin%20guide&view=list&page=1')


def scrape_page():
    threading.Timer(10.0, scrape_page).start() # recursively calls scrape function every 10 seconds
    print(f'"scrape called": {round(time.time() - start_time, 3)} seconds')
    print(html_text)
scrape_page()
