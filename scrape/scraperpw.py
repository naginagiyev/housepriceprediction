import os 
import time
import json

import warnings
warnings.filterwarnings("ignore")

from tqdm import tqdm
from playwright.sync_api import sync_playwright

scraped_data = []
error_count = 0

with open("ootlinks.txt", "r") as file:
    links = [link.strip() for link in file.readlines()]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    for link in tqdm(links, desc="Scraping Links"):
        one_data = {}
        
        try:
            page.goto(link)
            page.wait_for_selector("#js-search-results > div.page-content > div.product.bz-container.bz-mb-15 > div > main > section:nth-child(3) > div > div")
            price = page.locator("#js-search-results > div.page-content > div.product.bz-container.bz-mb-15 > div > aside > div > div.product-sidebar__box > div.product-price > div.product-price__i.product-price__i--bold > span.price-val").text_content()
            address = page.locator("#js-search-results > div.page-content > div.product-heading-container > div > div > div.product-heading__left.bz-d-flex.bz-align-center > h1").text_content().split(", ")[-1]
            error_count = 0
        
            latlong = page.locator("#item_map")
            lat = latlong.get_attribute('data-lat')
            lng = latlong.get_attribute('data-lng')

            one_data["latitude"] = lat
            one_data["longitude"] = lng
            one_data["price"] = price
            one_data["address"] = address
            
            detail_names = page.locator(".product-properties__i-name").all_text_contents()
            detail_values = page.locator(".product-properties__i-value").all_text_contents()

            for name, value in zip(detail_names, detail_values):
                key = name.strip().lower()
                one_data[key] = value.strip().lower()

            scraped_data.append(one_data)

        except:
            error_count += 1
            if error_count > 3:
                break
            else:
                time.sleep(5)
                continue

    with open('./data/ootdata.json', 'w', encoding="utf-8") as f:
        json.dump(scraped_data, f, indent=0)

    browser.close()

os.system("shutdown /s /f /t 0")