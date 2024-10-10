import requests
from bs4 import BeautifulSoup
import json
import time
import os
import boto3
from openai import OpenAI


def get_all():
    # URL of the PAW Patrol Season 1 wiki page
    urls = get_combined_urls()
    results = []
    for url in urls:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error if the request failed

        soup = BeautifulSoup(response.text, "html.parser")

        products = soup.find_all(
            "article", class_="product-miniature js-product-miniature"
        )
        for product in products:
            product_id = (
                product.find("p", class_="pl_reference").find("strong").text.strip()
            )

            product_url = product.find("h3", class_="h3 product-title").find("a")[
                "href"
            ]

            product_name = (
                product.find("h3", class_="h3 product-title").find("a").text.strip()
            )

            try:
                product_price = (
                    product.find("div", class_="product-price-and-shipping")
                    .find("span", "price")
                    .text.strip()
                )
            except:
                product_price = ""

            print(product_id, product_url, product_name, product_price)

            results.append(
                {
                    "name": product_name,
                    "price": product_price,
                    "url": product_url,
                    "product_id": product_id,
                }
            )

    json.dump(results, open("tukku_products.json", "w"), indent=2)

def get_combined_urls():
    categoryURLs = []
    urls = get_category_urls()
    for url in urls:
        maxPagenum = get_maxPage(url)
        categoryURLs.extend([f"{url}?page={k}" for k in range(1, maxPagenum + 1)])

    return categoryURLs

def get_category_urls():
    categoryUrls = []
    baseUrl = "https://tukku.net"
    response = requests.get(baseUrl)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    li_elements = soup.find_all('li', class_='mm_menus_li')
    for li in li_elements:
        a_tag = li.find('a')
        categoryUrls.append(a_tag.get('href'))
    return  categoryUrls


def get_maxPage(url):
    pageNums = []
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    page_ul = soup.find_all('ul', class_='page-list')
    for ul in page_ul:
        page_li = ul.find_all('li')
        for li in page_li:
            a_tag = li.find('a')
            if a_tag:
                text = a_tag.text.strip()
                try:
                    number = int(text)
                    pageNums.append(number)
                except ValueError:
                    pass
    return max(pageNums)


def get_individual():
    products = json.load(open("tukku_products.json"))

    for product in products:
        # if product["product_id"] != "06417783171836":
        #    continue

        if os.path.exists(f"tukku_data/{product['product_id']}.json"):
            continue

        product_info = product.copy()

        print(product_info)
        url = product["url"]
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # short description
        # description_short = soup.find("div", id="product-description-short").find("span").text.strip()

        # description
        description = soup.find("div", class_="product-description").find_all("p")
        description = "\n".join(p.get_text(strip=True) for p in description)
        if description == "":
            description = soup.find("div", class_="product-description").find_all("div")
            description = "\n".join(p.get_text(strip=True) for p in description)
        if description == "":
            description = product_info["name"]
            print("No description found!")

        # image link
        image_url = soup.find("img", class_="thumb js-thumb selected")[
            "data-image-large-src"
        ]

        try:
            # brand
            brand = soup.find("a", class_="editable").find("span").text.strip()
        except:
            brand = ""

        # add
        product_info["description"] = description
        # product_info["description_short"] = description_short
        product_info["image_url"] = image_url
        product_info["brand"] = brand

        json.dump(
            product_info,
            open(f"tukku_data/{product_info['product_id']}.json", "w"),
            indent=2,
        )

        time.sleep(2)


def translate():
    translator = boto3.client(
        service_name="translate", region_name="eu-west-1", use_ssl=True
    )

    for file in os.listdir("./tukku_data/"):

        if os.path.exists(f"./tukku_data_en/{file}"):
            continue

        data = json.load(open(f"./tukku_data/{file}"))
        name = data["name"]
        description = data["description"]

        print(data["product_id"])
        print(name)
        print(description)

        name_en = translator.translate_text(
            Text=name,
            SourceLanguageCode="fi",
            TargetLanguageCode="en",
        )["TranslatedText"]
        description_en = translator.translate_text(
            Text=description,
            SourceLanguageCode="fi",
            TargetLanguageCode="en",
        )["TranslatedText"]

        data["name_en"] = name_en
        data["description_en"] = description_en

        json.dump(data, open(f"./tukku_data_en/{file}", "w"), indent=2)
        time.sleep(1)


def get_information_from_image():

    for file in os.listdir("./tukku_data/"):

        if os.path.exists(f"./tukku_data_image_info/{file}"):
            continue

        data = json.load(open(f"./tukku_data/{file}"))
        image_url = data["image_url"]
        print(image_url)

        with OpenAI(
            api_key="sk-proj-Js6CGexnfUY9VqhlhEjrT3BlbkFJmxSsT5dFBOkfok4fnBVd"
        ) as client:

            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": "Describe the image with a lot of details. It's a product image from an online store. The generated description will be used to improve the search engine. Description should cover relevant information such as design, materials, patterns, color, functions, use occasions, lifestyle, size, etc. If there are multiple products in the image, please describe them all.",
                        },
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image_url",
                                    "image_url": {"url": image_url},
                                },
                            ],
                        },
                    ],
                    temperature=0.0,
                )

                result = response.choices[0].message.content

                image_data = {"image_information": result}

                json.dump(
                    image_data, open(f"./tukku_data_image_info/{file}", "w"), indent=2
                )
            except Exception as e:
                print(e)

        time.sleep(2)


#


if __name__ == "__main__":
    get_all()
    # get_individual()
    # translate()

    # Extract data from image
    # get_information_from_image()
