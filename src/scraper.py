import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3 import Retry


def get_session():
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))
    return session

def scrapePageUrls():
    pageURLs = []
    urls = scrape_category_urls()
    for url in urls:
        maxPagenum = get_maxPage(url)
        pageURLs.extend([f"{url}?page={k}" for k in range(1, maxPagenum + 1)])
    print("get all urls")
    return pageURLs

def scrape_category_urls():
    categoryUrls = []
    baseUrl = "https://tukku.net"
    session = get_session()
    response = session.get(baseUrl)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    li_elements = soup.find_all('li', class_='mm_menus_li')
    for li in li_elements:
        a_tag = li.find('a')
        categoryUrls.append(a_tag.get('href'))
    return  categoryUrls


def get_maxPage(url):
    pageNums = []
    session = get_session()
    response = session.get(url)
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