import threading
import time
from bs4 import BeautifulSoup


start_time = time.time()









def scrape_page():
    threading.Timer(10.0, scrape_page).start() # recursively calls scrape function every 10 seconds
    print(f'"scrape called": {round(time.time() - start_time, 2)} seconds')
    for i in range(100):
        print(i)

scrape_page()