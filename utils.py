import os
import sys
import requests
from bs4 import BeautifulSoup
import hashlib
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
import pymysql


def download_image(session, img_url, hashed_title):
    file_name = os.path.join("C:/workspace/woongsworld_module/WoongsWorld/news_imgs", hashed_title + ".jpg")
    try:
        response = session.get(img_url)
        with open(file_name, "wb") as f:
            f.write(response.content)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while trying to get {img_url}: {str(e)}")
    except Exception as e:
        print(f"An error occurred while trying to write the file {file_name}: {str(e)}")


def parse_news_page(session, url):
    try:
        response = session.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while trying to get {url}: {str(e)}")


def get_recent_news_ids(curs):
    try:
        curs.execute("SELECT news_id FROM news_pages ORDER BY created_date DESC LIMIT 35")
        recent_news_ids = [row['news_id'] for row in curs.fetchall()]
        return recent_news_ids
    except Exception as e:
        print(f"An error occurred while trying to fetch data from the database: {str(e)}")


def connect_db():
    conn = None
    curs = None
    try:
        conn = pymysql.connect(host='127.0.0.1', port=3308, user='root', password='1234', db='wworld', charset='utf8')
        curs = conn.cursor(pymysql.cursors.DictCursor)
    except Exception as e:
        print(f"An error occurred while trying to connect to the database: {str(e)}")

    return conn, curs


def close_db(conn):
    if conn is not None:
        try:
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"An error occurred while trying to close the database connection: {str(e)}")
