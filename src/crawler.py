import csv
import json
import random
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import scraper
import crawlAttributes


async def fetch_page(session, url, min_delay=0.1, max_delay=0.5, retries=3):
    for attempt in range(retries):
        try:
            async with session.get(url, timeout=15) as response:
                response.raise_for_status()
                await asyncio.sleep(random.uniform(min_delay, max_delay))
                return await response.text()
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            print(f"Attempt {attempt + 1} failed for {url}: {e}")
            if attempt == retries - 1:
                print(f"Failed to fetch {url} after {retries} attempts.")
                return None
            await asyncio.sleep(2 ** attempt)  # Exponential backoff


async def process_page(session, curPage, results, count, products_num):
    page_content = await fetch_page(session, curPage)
    if page_content:
        soup = BeautifulSoup(page_content, "html.parser")
        products_on_page = soup.find_all("article", class_="product-miniature js-product-miniature")

        for product in products_on_page:
            # await crawlAttributes.get_common_attributes(product, soup)
            product_data = {
                "name": product.find("h3", class_="product-title").get_text(strip=True),
                "url": product.find("a")["href"],
                "product_id": product.get("data-id-product", ""),
            }
            count[0] += 1
            print(f"{count[0]}/{products_num} ({(count[0] / products_num) * 100:.2f}%)")
            results.append(product_data)
    else:
        print(f"Skipping {curPage} due to repeated failures.")


async def get_all():
    page_urls = scraper.scrapePageUrls()
    # page_urls = ["https://tukku.net/586-hiusnaamiot-ja-tehohoidot?page=2"]  # test this one only
    results = []
    products_num = len(page_urls) * 56  # Assuming 56 products per page
    count = [0]

    # Limit the number of concurrent requests to 10
    semaphore = asyncio.Semaphore(10)
    async with aiohttp.ClientSession() as session:
        tasks = [
            process_page_with_semaphore(semaphore, session, curPage, results, count, products_num)
            for curPage in page_urls
        ]
        await asyncio.gather(*tasks)

    # Save in CSV file
    # with open('output.csv', mode='w', newline='', encoding='utf-8') as file:
        # writer = csv.writer(file)
        # writer.writerows(results)
    # Save all results to a JSON file after all pages are processed
    with open("tukku_products_all.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


async def process_page_with_semaphore(semaphore, session, curPage, results, count, products_num):
    async with semaphore:
        await process_page(session, curPage, results, count, products_num)

async def get_product_detail(prodct):

    return

async def process_product(session, product,productsAmount, count):
    product_content = await fetch_page(session, product["url"])
    if product_content:
        soup = BeautifulSoup(product_content, "html.parser")
        await crawlAttributes.get_common_attributes(product, soup)
        count[0] += 1
        print(f"{count[0]}/{productsAmount} ({(count[0] / productsAmount) * 100:.2f}%)" )

async def process_product_with_semaphore(semaphore, session, product, productsAmount, count):
    async with semaphore:
        await process_product(session, product, productsAmount, count)

async def get_individual():
    # read product all
      with open("tukku_products_all.json", "r", encoding="utf-8") as f:
        products = json.load(f)
        semaphore = asyncio.Semaphore(20)
        productsAmount = len(products)
        count = [0]

        async with aiohttp.ClientSession() as session:
            tasks = [
                process_product_with_semaphore(semaphore, session, product, productsAmount, count)
                for product in products
            ]
            await asyncio.gather(*tasks)
            with open("tukku_products_detail_all.json", "w", encoding="utf-8") as f:
                json.dump(products, f, ensure_ascii=False, indent=2)



    # get product url, fetch product url detail page
    # get common attributes
    # optional - translation and call ollama to get product specific attributes


if __name__ == "__main__":
    # asyncio.run(get_all())
    # asyncio.run(get_individual())
