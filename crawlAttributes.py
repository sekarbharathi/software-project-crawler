import json
import asyncio
from audioop import error

import requests
from bs4 import BeautifulSoup
import re
# Todo: Add try catch to handle no value
def getAttributes(url):
    products = json.load(open("tukku_products_category.json"))
    for index, product in enumerate(products):
        if index<1:
            url = product['url']
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            get_common_attributes(product, soup)

    with open("tukku_products_detail_category.json", "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)


async def get_common_attributes(product, soup):

    await asyncio.gather(
        get_image_url(product, soup),
        get_brand(product, soup),
        get_delivery_time(product, soup),
        get_price(product, soup),
        get_discount(product, soup),
        get_description(product, soup),
        get_stock(product, soup),
        get_category(product, soup),
        get_review_and_rating(product, soup)
    )


async def get_review_and_rating(product, soup):
    try:
        reviews = soup.find("div", class_="comments_note").find("span", class_="nb-comments").get_text(strip=True)
        star_rating = len(soup.find("div", class_="star_content").find_all("div", class_="star"))
    except:
        reviews = "No reviews"
        star_rating = 0
    product["star_rating"] = star_rating
    product["reviews"] = reviews


async def get_description(product, soap):
    descriptions = soap.find("div", class_="product-description").find_all("p")
    description = "\n".join(p.get_text(strip=True) for p in descriptions)
    if description == "":
        description = soap.find("div", class_="product-description").find_all("div")
        description = "\n".join(p.get_text(strip=True) for p in description)
    if description == "":
        description = product["name"]
    product["description"] = description

async def get_image_url(product, soup):
    image_url = ""
    try:
        img_tag = soup.find("img", class_="js-qv-product-cover")
        image_url = img_tag["src"] if img_tag else ""

    except error as e:
        image_url=""
        print(f"exception{e}")
    product["image_url"]=image_url

async def get_category(product, soup):
    breadcrumn = soup.find("nav", class_="breadcrumb")
    if breadcrumn:
        categories = [span.get_text(strip=True) for span in breadcrumn.find_all("span", itemprop="name")]
    else:
        categories = []
    product["categories"] = categories
async def get_name(product, soap):
    product["name"] = (
        soap.find("h3", class_="h3 product-title").find("a").text.strip()
    )

async def get_id(product, soap):
    product["id"] = (
        soap.find("p", class_="pl_reference").find("strong").text.strip()
    )

async def get_url(product, soap):
    product["url"] = soap.find("h3", class_="h3 product-title").find("a")[
        "href"
    ]

async def get_price(product, soup):
    try:
        price_span = soup.find("div", class_="current-price") or \
                     soup.find("span", class_="price")
        product_price = price_span.get_text(strip=True) if price_span else ""
    except Exception as e:
        print(f"Error extracting price: {e}")
        product_price = ""
    product["price"] = product_price


async def get_brand(product, soup):
    try:
        # Locate the div containing the brand information
        brand_div = soup.find("div", class_="product-manufacturer")
        if brand_div:
            # Locate the anchor tag within the div
            brand_anchor = brand_div.find("a")
            if brand_anchor:
                # Extract the brand name from the anchor tag's text
                brand_text = brand_anchor.get_text(strip=True)
            else:
                brand_text = ""
        else:
            brand_text = ""
    except Exception as e:
        print(f"Error extracting brand: {e}")
        brand_text = ""

    # Assign the extracted brand to the product dictionary
    product["brand"] = brand_text

async def get_delivery_time(product, soap):
    try:
        delivery = soap.find("span", id="product-availability").text.strip()
        delivery_time = re.search(r'\b\d+(\.\d+)?\b', delivery)
        delivery_time = delivery_time.group(0) if delivery_time else None
        product["delivery"] =delivery_time
    except Exception as e:
        print(e)

async def get_discount(product, soap):
    discount = soap.find("span", class_="discount discount-amount")
    discount = discount.text.strip() if discount else None
    match = re.search(r'\d+,\d+', discount) if discount else None
    product["discount"] = match.group(0) if match else None

async def get_stock(product, soap):
    stock = soap.find("span", {'data-stock': True})
    stock_value = stock['data-stock'] if stock else None
    product["stock"] = stock_value

# the common attributes are id, name, description, price, category, brand, stock, discount , delivery_time

# def getCommonAttributes(url):
#
# # other attributes
# def getSpecificAttributes(url):

if __name__ == "__main__":
    getAttributes('')