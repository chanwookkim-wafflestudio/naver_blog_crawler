import requests
from bs4 import BeautifulSoup

URL = 'https://blog.naver.com/lovable_d/221230008776'
HOST = 'https://blog.naver.com'


def get_url(blog_url):
    res = requests.get(blog_url)
    soup = BeautifulSoup(res.text, 'html.parser')
    frame_tag = soup.find_all(id='mainFrame')
    content_url = HOST + frame_tag[0]['src']

    res = requests.get(content_url)
    soup = BeautifulSoup(res.text, 'html.parser')
    text_tag_list = soup.select('p.se_textarea > span')

    for text_tag in text_tag_list:
        for string in text_tag.strings:
            print(string)


def main():
    get_url(URL)


if __name__ == "__main__":
    main()
