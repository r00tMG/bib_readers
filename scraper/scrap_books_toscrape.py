import time, re, csv
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By

# ---- Configurer le navigateur ----
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # optionnel
driver = webdriver.Chrome(options=options)

url_base = "https://books.toscrape.com/catalogue/"
driver.get("https://books.toscrape.com/")

books_data = []

def extract_rating(rating_text):
    mapping = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    return mapping.get(rating_text, 0)

# ---- Parcourir toutes les pages ----
while True:
    books = driver.find_elements(By.CSS_SELECTOR, ".product_pod h3 a")

    for b in books:
        link = b.get_attribute("href")
        driver.execute_script("window.open(arguments[0]);", link)
        driver.switch_to.window(driver.window_handles[-1])

        # ---- Extraire données ----
        try:
            title = driver.find_element(By.TAG_NAME, "h1").text.strip()
        except:
            title = "N/A"

        try:
            desc = driver.find_element(By.CSS_SELECTOR, "#product_description + p").text.strip()
        except:
            desc = title  # fallback

        price = driver.find_element(By.CSS_SELECTOR, ".price_color").text
        price = float(price.replace("£", "").strip())

        availability = driver.find_element(By.CSS_SELECTOR, ".instock.availability").text
        avail_num = int(re.search(r"\d+", availability).group()) if re.search(r"\d+", availability) else 0

        try:
            rating_class = driver.find_element(By.CSS_SELECTOR, "p.star-rating").get_attribute("class").split()[-1]
            rating = extract_rating(rating_class)
        except:
            rating = 0

        try:
            img_url = driver.find_element(By.CSS_SELECTOR, ".thumbnail img").get_attribute("src")
        except:
            img_url = ""

        books_data.append({
            "title": title,
            "description": desc,
            "price": price,
            "availability": avail_num,
            "rating": rating,
            "image_url": img_url
        })

        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    # ---- Page suivante ----
    try:
        next_btn = driver.find_element(By.CSS_SELECTOR, ".next a").get_attribute("href")
        driver.get(next_btn)
    except:
        break

driver.quit()

# ---- Sauvegarder CSV ----
df = pd.DataFrame(books_data)
df.to_csv("livres_bruts.csv", index=False, encoding="utf-8")
print(" Données sauvegardées dans livres_bruts.csv")
