import urllib.parse

from bs4 import BeautifulSoup
import requests
from GLOBAL_CONFIG import CONFIG
import random
from logs import capture_error

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.203"
# Crear una sesión y configurar el agente de usuario y las cookies
session = requests.Session()
session.headers.update({
    "User-Agent": user_agent
})

cookie_value = ''
cookie_initial = '2JBkEw%7Ck0GmCN'
for letter in range(len(cookie_initial)):
    cookie_value += random.choice(cookie_initial)

session.cookies.set("recent", cookie_value, domain=".is.gd", path="/")


def start_shorter():

    try:
        with open(CONFIG.PATH_URLS_START) as urls:
            for url in urls.readlines():
                url = str(url).strip()
                if url != "":
                    url = urllib.parse.quote(url)
                    # Header for request
                    headers = {
                        'user-agent': user_agent,
                        'authority': 'is.gd',
                        'referrer': 'https://is.gd/create.php',
                        'credentials': 'omit',
                        'mode': 'cors',
                        'content-type': 'application/x-www-form-urlencoded'
                    }
                    # Body for request the short url
                    body = f'url={url}&shorturl=&opt=0'
                    # send request
                    response_html = requests.post(CONFIG.URL_PAGE_OFFICE, headers=headers, data=body)
                    # updating session cookie
                    session.cookies.set("recent", response_html.cookies.get('recent'), domain=".is.gd", path="/")
                    # converter to HTML content, for then work with that
                    bs = BeautifulSoup(response_html.content, 'html.parser')
                    # get url
                    try:
                        url_shorter = bs.find('input', attrs={'id': 'short_url'}).get('value')
                    except Exception as error:
                        capture_error(str(error), 'Error to get short url')
                    # save short url
                    with open(CONFIG.PATH_URLS_END, 'a') as urls_end:
                        urls_end.write(url_shorter + '\n')
                        # show short url
                        print(url_shorter)
    except Exception as error:
        capture_error(str(error), 'Open File Error')

