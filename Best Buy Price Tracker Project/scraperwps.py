import requests
from bs4 import BeautifulSoup
import json
import re
import os
from plyer import notification  # for desktop notifications
import smtplib
from email.message import EmailMessage

##################################################################################################################
# Scraper V3 Checks price and stock of item(s). Allows email notifications to be sent if price or stock changes. #
##################################################################################################################

# ---------- CONFIG ----------
PRICE_HISTORY_FILE = "bestbuy_price_history.json"

# Email notification settings (optional)
EMAIL_ALERTS = False  # Set True to enable email alerts
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = "your_email@gmail.com"
EMAIL_PASS = "your_email_app_password"
EMAIL_TO = "recipient_email@gmail.com"

# List of products to track
PRODUCT_URLS = [
    "https://www.bestbuy.ca/en-ca/product/asus-rog-astral-geforce-rtx-5090-oc-edition-32gb-video-card/19177947",
    "https://www.bestbuy.ca/en-ca/product/pny-nvidia-geforce-rtx-5080-graphics-card-16gb-gddr7-2-30ghz-core-2-62ghz-boost-256-bit-pcie-5-0-x16-hdmi-3x-displayport/19469251",
    # Add more URLs here
]

# ---------- FUNCTIONS ----------
def fetch_product_data(url):
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

    script_tag = None
    for s in soup.find_all("script"):
        if s.string and "window.__INITIAL_STATE__" in s.string:
            script_tag = s.string
            break

    if not script_tag:
        return None

    match = re.search(r"window\.__INITIAL_STATE__\s*=\s*(\{.*\});", script_tag)
    if not match:
        return None

    data_json = json.loads(match.group(1))
    prod = data_json.get('product', {}).get('product', {})

    if not prod:
        return None

    title = prod.get("name")
    price = prod.get("regularPrice") or prod.get("priceWithEhf") or prod.get("priceWithoutEhf")
    is_on_sale = prod.get("isOnSale", False)
    saving = prod.get("saving")
    in_stock = True
    if prod.get("isPreorderable") or prod.get("isClearance") or prod.get("availability", {}).get("isAvailabilityError"):
        in_stock = False
    availability = "In Stock" if in_stock else "Out of Stock"

    return {
        "title": title,
        "price": price,
        "on_sale": is_on_sale,
        "saving": saving,
        "availability": availability,
        "url": url
    }

def send_desktop_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        timeout=10  # seconds
    )

def send_email_notification(subject, body):
    if not EMAIL_ALERTS:
        return
    msg = EmailMessage()
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_TO
    msg['Subject'] = subject
    msg.set_content(body)
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(msg)

# ---------- LOAD PRICE HISTORY ----------
if os.path.exists(PRICE_HISTORY_FILE):
    with open(PRICE_HISTORY_FILE, "r") as f:
        price_history = json.load(f)
else:
    price_history = {}

# ---------- TRACK PRODUCTS ----------
for url in PRODUCT_URLS:
    data = fetch_product_data(url)
    if not data:
        print(f"Failed to retrieve product info for {url}")
        continue

    title = data['title']
    price = data['price']
    availability = data['availability']

    print(f"\nProduct: {title}")
    print(f"Price: ${price}")
    print(f"Availability: {availability}")
    if data['on_sale']:
        print(f"On Sale! You save: ${data['saving']}")

    # Check previous data
    previous = price_history.get(url)
    alert_msgs = []

    if previous:
        prev_price = previous.get("price")
        prev_avail = previous.get("availability")
        if price and prev_price and price < prev_price:
            alert_msgs.append(f"Price dropped! Previous: ${prev_price}, Now: ${price}")
        if prev_avail != availability:
            alert_msgs.append(f"Stock change! Previous: {prev_avail}, Now: {availability}")

    # Send alerts if any
    if alert_msgs:
        message = f"{title}\n" + "\n".join(alert_msgs)
        send_desktop_notification("BestBuy Alert", message)
        send_email_notification(f"BestBuy Alert: {title}", message)

    # Update history
    price_history[url] = {"price": price, "availability": availability}

# ---------- SAVE HISTORY ----------
with open(PRICE_HISTORY_FILE, "w") as f:
    json.dump(price_history, f, indent=2)

print("\nTracking complete.")
