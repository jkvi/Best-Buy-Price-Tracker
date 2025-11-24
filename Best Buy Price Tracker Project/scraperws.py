import requests
from bs4 import BeautifulSoup
import json
import re

##############################################
# Scraper V2 with stock/availability checker #
##############################################

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

    # Find JSON in script tag
    script_tag = None
    for s in soup.find_all("script"):
        if s.string and "window.__INITIAL_STATE__" in s.string:
            script_tag = s.string
            break

    if not script_tag:
        print("Error: Could not find BestBuy JSON in script tag.")
        return None

    match = re.search(r"window\.__INITIAL_STATE__\s*=\s*(\{.*\});", script_tag)
    if not match:
        print("Error: Could not extract JSON object.")
        return None

    data_json = json.loads(match.group(1))

    try:
        prod = data_json['product']['product']

        # Product title
        title = prod.get("name")

        # Price
        price = prod.get("regularPrice") or prod.get("priceWithEhf") or prod.get("priceWithoutEhf")

        # Sale info
        is_on_sale = prod.get("isOnSale", False)
        saving = prod.get("saving")  # amount saved if on sale

        # Stock availability
        in_stock = True
        if prod.get("isPreorderable") or prod.get("isClearance") or prod.get("availability", {}).get("isAvailabilityError"):
            in_stock = False

        availability = "In Stock" if in_stock else "Out of Stock"

        return {
            "title": title,
            "price": price,
            "on_sale": is_on_sale,
            "saving": saving,
            "availability": availability
        }

    except Exception as e:
        print("Parsing error:", e)
        return None

# -------------------------
# RUN SCRAPER
# -------------------------

URL = "https://www.bestbuy.ca/en-ca/product/asus-rog-astral-geforce-rtx-5090-oc-edition-32gb-video-card/19177947"
result = get_bestbuy_info(URL)

if result:
    print("Product:", result['title'])
    print("Price: $", result['price'])
    print("Availability:", result['availability'])
    if result['on_sale']:
        print(f"On Sale! You save: ${result['saving']}")
else:
    print("Failed to retrieve product information.")
