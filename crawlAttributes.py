from openai import OpenAI
import json
import requests
from bs4 import BeautifulSoup
import re
import  ollama
# Todo: Add try catch to handle no value
def getAttributes(url):
    products = json.load(open("tukku_products.json"))
    for index, product in enumerate(products):
        if index<1:
            url = product['url']
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            get_common_attributes(product, soup)
            get_specific_attibute(product, soup)

    with open("tukku_products_all.json", "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)


def get_common_attributes(product, soup):
    get_image_url(product, soup)
    get_band(product, soup)
    get_delivery_time(product, soup)
    get_discount(product, soup)
    get_description(product, soup)
    get_stock(product, soup)

def get_specific_attibute(product, soup):
    from openai import OpenAI
    with OpenAI(
            api_key="sk-6Kdct2IBYgkgvEie96E2C33dF5D0484dB80d9a9674DfFf41",
            base_url="https://ai-yyds.com/v1"
    ) as client:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Based on the description I give, please return key-value string pairs supporting search engine searching with related products. No name and description required. Make sure the output contains no escape characters or additional formatting. Do not include backslashes or any unnecessary characters. List at most 10 specifications that buyers care about when purchasing this kind of product. Keep it short and concise. Only return the dictionary itself, and the language should be English.This is the description:" + product['description'],
                }
            ],
            temperature=0.0,
        )
        result = re.sub(r"\\", "",  response.choices[0].message.content)
        print(result)
        product['attributes'] = result

def get_specific_attribute_ollama():
    url = "http://195.148.30.36:11434/api/generate"
    data = {
        "model": "",  # Specify the model you deployed
        "prompt": "Explain the concept of machine learning in simple terms."
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        # Parse the response JSON
        result = response.json()
        print("Response:", result['text'])  # Output the text generated by the model
    else:
        print(f"Error: {response.status_code}, {response.text}")

def get_description(product, soap):
    description = soap.find("div", class_="product-description").find_all("p")
    description = "\n".join(p.get_text(strip=True) for p in description)
    if description == "":
        description = soap.find("div", class_="product-description").find_all("div")
        description = "\n".join(p.get_text(strip=True) for p in description)
    if description == "":
        description = product["name"]
    product["description"] = description

def get_image_url(product, soap):
    product["image_url"] = soap.find("img", class_="thumb js-thumb selected")[
        "data-image-large-src"
    ]

def get_band(product, soap):
    product["brand"] = soap.find("a", class_="editable").find("span").text.strip()

def get_delivery_time(product, soap):
    delivery = soap.find("span", id="product-availability").text.strip()
    delivery_time = re.search(r'\b\d+(\.\d+)?\b', delivery)
    delivery_time = delivery_time.group(0) if delivery_time else None
    product["delivery"] =delivery_time

def get_discount(product, soap):
    discount = soap.find("span", class_="discount discount-amount")
    discount = discount.text.strip() if discount else None
    match = re.search(r'\d+,\d+', discount) if discount else None
    product["discount"] = match.group(0) if match else None

def get_stock(product, soap):
    stock = soap.find("span", {'data-stock': True})
    stock_value = stock['data-stock'] if stock else None
    product["stock"] = stock_value

# the common attributes are id, name, description, price, category, brand, stock, discount , delivery_time

# def getCommonAttributes(url):
#
# # other attributes
# def getSpecificAttributes(url):

if __name__ == "__main__":
    # getAttributes('')
    get_specific_attribute_ollama()