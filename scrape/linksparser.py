import time
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

chrome_options = Options()
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()
wait = WebDriverWait(driver, 10)

all_hrefs = set()

for page in tqdm(range(1, 566), desc="Gathering links"):
    try:
        driver.get(f"https://bina.az/baki/alqi-satqi/menziller?page={page}")
        driver.execute_script("window.scrollBy(0, 2000);")
        time.sleep(1)

        items_list = None
        for _ in range(3):
            try:
                items_list = wait.until(EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "#js-items-search > div.items_list")))
                break
            except Exception as e:
                print(f"ERROR: {e}. Trying again...")
                time.sleep(1)
                continue

        if not items_list:
            continue

        links = items_list.find_elements(By.TAG_NAME, "a")
        hrefs = {link.get_attribute("href") for link in links if link.get_attribute("href") and 
                 link.get_attribute("href").startswith("https://bina.az/items/")}
        all_hrefs.update(hrefs)

    except Exception as e:
        print(f"ERROR: {e}")
        continue

driver.quit()

with open("ootlinks.txt", "w", encoding="utf-8") as file:
    for href in all_hrefs:
        file.write(href + "\n")