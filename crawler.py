import requests
from bs4 import BeautifulSoup, element
import psycopg2
from settings import CONNECTION_ARGUMENTS
import sys

URL = 'https://blog.naver.com/kehkeh0422/221230876380'
HOST = 'https://blog.naver.com'


def connect_to_db():
    return psycopg2.connect(**CONNECTION_ARGUMENTS)


def get_data(blog_url):
    username, post_id = blog_url[23:].split('/')

    # Getting main frame url
    res = requests.get(blog_url)
    soup = BeautifulSoup(res.text, 'html.parser')
    frame_tag = soup.find_all(id='mainFrame')
    content_url = HOST + frame_tag[0]['src']

    res = requests.get(content_url)
    soup = BeautifulSoup(res.text, 'html.parser')

    # check smart editor
    editor_tags = soup.select('p.write_by_smarteditor3')
    if len(editor_tags) == 0:
        raise Exception('Warning: not written by smarteditor3, so just skip.')


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


def insert_data(cur, data):
    cur.execute(
        "INSERT INTO blog_post (post_id, username, title, body_raw, body) VALUES (%s, %s, %s, %s, %s)", (
            data['post_id'], data['username'], data['title'], data['body_raw'], data['body']))


def main():
    if len(sys.argv) < 2:
        raise ReferenceError('Please input blog urls to execute.')

    connection = connect_to_db()
    cursor = connection.cursor()
    urls = sys.argv[1:]
    for idx, blog_url in enumerate(urls):
        print('[%d/%d]: %s' % (idx + 1, len(urls), blog_url))
        try:
            data = get_data(blog_url)
            insert_data(cursor, data)
            connection.commit()
        except Exception as e:
            print(e)

    connection.close()


if __name__ == "__main__":
    main()
