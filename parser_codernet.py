import requests
from bs4 import BeautifulSoup
import os
from multiprocessing import Pool
from selenium import webdriver
import time

site = 'https://codernet.ru'
CATEGORY = {}
count = 0
session = requests.Session()
session.headers = headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build / MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Mobile Safari/537.36",
    "Accept-Language": 'ru'
    }

# PARSE CATEGORY PROGRAM
def init_session_lang():
    url = 'https://codernet.ru/books/'
    result = session.get(url=url)
    result.raise_for_status()
    parse_category(result.text)


def parse_category(text: str):
    soup = BeautifulSoup(text, 'lxml')
    category = soup.find_all('a', attrs={'class': 'list-group-item text-dark'})
    for cat in category:
        CATEGORY[cat.text] = site + cat.get('href')

def get_all_links(choose_books, lst):
    url_on_book = []
    new_lst = []

    for i in range(len(lst)):
        new_lst += lst[i]

    for book in choose_books:
        url_on_book.append(new_lst[int(book)])

    return url_on_book


# PARSE URLS
def parse_urls_download_page(url_page):
    global count
    total = 1
    lst = []
    for i in range(5):
        req = session.get(url_page + f'?page={total}')
        req.raise_for_status()
        soup = BeautifulSoup(req.text, 'lxml')
        info_books = soup.find_all('h5', attrs={'class': 'mt-0'})
        for info_book in info_books:
            data = site + info_book.a.get('href')
            if data not in lst:
                print(f'[{count}] --- {info_book.p.text}')
                count += 1
                lst.append(str(data))
            else:
                break
        total += 1

    return lst

#Download

def get_html(url):
    r = session.get(url=url, stream=True)
    r.raise_for_status()
    return r

def download_book(url):
    html = get_html(url)
    title = get_page_url_download(html)

    get_download(url, title)

def get_download(url, title):
    base_dir = os.path.dirname(os.path.realpath(__file__))
    driver = webdriver.Chrome(executable_path=base_dir + '\chromedriver.exe')
    driver.get(url)
    button = driver.find_element_by_xpath('//a[@class="btn btn-outline-secondary"]')
    button.click()
    time.sleep(30)

    driver.quit()
    print('Files successfully installed.')

def get_page_url_download(html):
    soup = BeautifulSoup(html.text, 'lxml')
    title = soup.find('div', attrs={'class': 'col-sm-9'})
    down_url = soup.find('a', attrs={'class' : 'btn btn-outline-secondary', 'target': '_blank'})

    if down_url == '':
        print('Fail download')
    else:
        print(title.h1.text)
        print(site + down_url.get('href'))

    return title.h1.text


# INFORMATION
def information(urls_numb):
    lst = []
    language_code = input(
        'Which programming language you want?(Write number through a space)\n')
    if language_code != '':
        new_lang = str(language_code).split(' ')
        for url in new_lang:
            if url.isdigit() and (int(url) >= 0 and int(url) <= 20):
                url_page = urls_numb[int(url)]
                a = parse_urls_download_page(url_page)
                lst.append(a)
                print('-' * 10)
                print('-' * 10)
                print('-' * 10)
                print('-' * 10)
            elif url == ' ':
                pass
            else:
                print('')
                print('-' * 10)
                print('')
                print('-' * 10)
                print('')

    choose_books = str(input('Which book do you want?(Write number through a space) \n')).split(' ')
    all_links = get_all_links(choose_books, lst)

    with Pool(4) as p:
        p.map(download_book, all_links)


def create_norm_number_url():
    urls = {}
    total = 0
    for key in CATEGORY:
        print(f'[{total}]-{key}')
        urls[total] = CATEGORY[key]
        total += 1
    return urls


def main():
    print('-' * 20)
    print('Welcome to the best code books parser')
    print('-' * 20)

    init_session_lang()
    urls = create_norm_number_url()

    information(urls)


if __name__ == '__main__':
    main()