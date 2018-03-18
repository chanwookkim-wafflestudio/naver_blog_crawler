import requests
from bs4 import BeautifulSoup, element
import psycopg2

URL = 'https://blog.naver.com/kehkeh0422/221230876380'
HOST = 'https://blog.naver.com'


def connect_to_db():
    return psycopg2.connect(dbname="naver", user="naver@castcoin-postgre", password="ckdxhdtjf",
                            host="naver.devluci.com")


def get_data(blog_url):
    username, post_id = blog_url[23:].split('/')

    # Getting main frame url
    res = requests.get(blog_url)
    soup = BeautifulSoup(res.text, 'html.parser')
    frame_tag = soup.find_all(id='mainFrame')
    content_url = HOST + frame_tag[0]['src']

    res = requests.get(content_url)
    soup = BeautifulSoup(res.text, 'html.parser')
    textarea_tag_list = soup.select('p.se_textarea')

    # getting body
    body = ''

    for idx, textarea_tag in enumerate(textarea_tag_list):
        for child in textarea_tag.descendants:
            if type(child) == element.NavigableString:
                body = body + child
            elif type(child) == element.Tag and child.name == 'br':
                body = body + '\n'
        if idx != len(textarea_tag_list) - 1:
            body = body + '\n\n'

    # getting body_raw
    body_raw = str(soup)

    # getting title
    title_parent_tag = soup.select('div.se_editView.se_title .se_textarea')[0]
    title = list(title_parent_tag.strings)[1]

    return {
        "username": username,
        "post_id": post_id,
        "body": body,
        "body_raw": body_raw,
        "title": title,
    }


def insert_data(connection, data):
    cur = connection.cursor()
    cur.execute("INSERT INTO naver_post (post_id, username, title, body_raw, body) VALUES (%s, %s, %s, %s, %s)" % (
        data['post_id'], data['username'], data['body'], data['body_raw'], data['title']))
    cur.close()


def main():
    connection = connect_to_db()
    data = get_data(URL)
    insert_data(connection, data)
    connection.close()


if __name__ == "__main__":
    main()
