import requests
from bs4 import BeautifulSoup
import json
import re

###################################################
# Scraper V1 - checks price of item from Best Buy #
###################################################

def get_bestbuy_info(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    # Find script containing window.__INITIAL_STATE__
    script_tag = None
    for s in soup.find_all("script"):
        if s.string and "window.__INITIAL_STATE__" in s.string:
            script_tag = s.string
            break

    if not script_tag:
        print("Error: Could not find BestBuy JSON in script tag.")
        return None

    # Extract JSON
    match = re.search(r"window\.__INITIAL_STATE__\s*=\s*(\{.*\});", script_tag)
    if not match:
        print("Error: Could not extract JSON object.")
        return None

    data_json = json.loads(match.group(1))

    try:
        prod = data_json['product']['product']

        # Get title
        title = prod.get("name")

        # Get price
        price = prod.get("regularPrice") or prod.get("priceWithEhf") or prod.get("priceWithoutEhf")

        return title, price

    except Exception as e:
        print("Parsing error:", e)
        return None

# -------------------------
# RUN SCRAPER
# -------------------------

URL = "https://www.bestbuy.ca/en-ca/product/asus-rog-astral-geforce-rtx-5090-oc-edition-32gb-video-card/19177947"
result = get_bestbuy_info(URL)

if result:
    title, price = result
    print("Product:", title)
    print("Price: $", price)
else:
    print("Failed to retrieve product information.")
