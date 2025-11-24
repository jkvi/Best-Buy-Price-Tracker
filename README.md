# Best-Buy-Price-Tracker

---

## What This Script Does (High-Level Overview)

This is a **BestBuy price and stock tracker**. Its main purpose is to:

1. Go to one or more BestBuy product pages.
2. Check the product **title, price, stock status, and sale info**.
3. Compare the current price and stock to the **last time you checked**.
4. Notify you if the price drops or stock changes (desktop alert or email).
5. Save a **history of prices** in a file so you can track changes over time.

I have included 3 versions.
scraper.py is the first working version that I made.
scraperws.py is an upgraded version with stock/availabilty checker.
scraperwps.py is the final version with everything included before but allows multiple items and optional email notifications.

I came up with the idea to create this project from https://www.youtube.com/watch?v=Bg9r_yLk7VY. Due to Amazon blocking automated scraping, I decided to create a scraper for BestBuy instead.

---

## Step-By-Step Explanation

### 1. Imports

```python
import requests
from bs4 import BeautifulSoup
import json
import re
import os
from plyer import notification
import smtplib
from email.message import EmailMessage
```

* `requests` → Download the webpage HTML.
* `BeautifulSoup` → Helps navigate the HTML.
* `json` → Read JSON data embedded in the page.
* `re` → Regular expressions for finding text patterns.
* `os` → Check if files exist.
* `plyer.notification` → Show desktop notifications.
* `smtplib` & `EmailMessage` → Send emails if price/stock changes.

---

### 2. Configuration

```python
PRICE_HISTORY_FILE = "bestbuy_price_history.json"
EMAIL_ALERTS = False  # enable email alerts
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = "your_email@gmail.com"
EMAIL_PASS = "your_email_app_password"
EMAIL_TO = "recipient_email@gmail.com"
```

* `PRICE_HISTORY_FILE` → File storing previous prices/availability.
* `EMAIL_ALERTS` → Turn email alerts on/off.
* `SMTP_*` and `EMAIL_*` → Email settings.

---

### 3. Products List

```python
PRODUCT_URLS = [
    "https://www.bestbuy.ca/.../19177947",
    "https://www.bestbuy.ca/.../19469251",
]
```

* List of product URLs to track.
* Add more URLs to track multiple products.

---

### 4. Function: fetch_product_data

```python
def fetch_product_data(url):
    ...
```

**Steps inside this function:**

1. **Download the page:**

```python
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")
```

2. **Find the JSON containing product info:**

```python
for s in soup.find_all("script"):
    if s.string and "window.__INITIAL_STATE__" in s.string:
        script_tag = s.string
        break
```

3. **Extract JSON from script:**

```python
match = re.search(r"window\.__INITIAL_STATE__\s*=\s*(\{.*\});", script_tag)
data_json = json.loads(match.group(1))
prod = data_json.get('product', {}).get('product', {})
```

4. **Extract useful fields:**

```python
title = prod.get("name")
price = prod.get("regularPrice") or prod.get("priceWithEhf") or prod.get("priceWithoutEhf")
is_on_sale = prod.get("isOnSale", False)
saving = prod.get("saving")
in_stock = True
if prod.get("isPreorderable") or prod.get("isClearance") or prod.get("availability", {}).get("isAvailabilityError"):
    in_stock = False
availability = "In Stock" if in_stock else "Out of Stock"
```

5. **Return data:**

```python
return {
    "title": title,
    "price": price,
    "on_sale": is_on_sale,
    "saving": saving,
    "availability": availability,
    "url": url
}
```

---

### 5. Functions for Notifications

```python
def send_desktop_notification(title, message):
    notification.notify(title=title, message=message, timeout=10)

def send_email_notification(subject, body):
    if not EMAIL_ALERTS:
        return
    ...
```

* `send_desktop_notification` → Shows a popup on your desktop.
* `send_email_notification` → Sends an email if price/stock changed.

---

### 6. Load Previous Prices

```python
if os.path.exists(PRICE_HISTORY_FILE):
    with open(PRICE_HISTORY_FILE, "r") as f:
        price_history = json.load(f)
else:
    price_history = {}
```

* Loads previous prices from a file.
* If the file doesn’t exist, starts fresh.

---

### 7. Track Products

```python
for url in PRODUCT_URLS:
    data = fetch_product_data(url)
    ...
```

For each product:

1. Fetch current product info.
2. Print title, price, stock, sale info.
3. Compare with previous price/stock.
4. Send notifications if needed.
5. Update price history.

---

### 8. Save Updated Price History

```python
with open(PRICE_HISTORY_FILE, "w") as f:
    json.dump(price_history, f, indent=2)
```

* Saves the latest price and stock info for future comparisons.

---

## ✅ Summary

This script is a **BestBuy product tracker** that:

* Scrapes product pages for **title, price, stock status, and sale info**.
* **Compares current data** to previous data stored in a file.
* Sends **alerts** when price drops or stock changes (desktop/email).
* Can track **multiple products at once**.
* Maintains a **persistent price history** in a JSON file.

It’s basically an automated way to watch BestBuy products so you don’t miss a sale or stock restock.
