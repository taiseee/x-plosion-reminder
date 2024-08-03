import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def run(event, context):
    current_time = datetime.now().time()
    logger.info("Your cron function ran at " + str(current_time))

    # URLからHTMLコンテンツを取得
    url = "https://store.x-plosion.jp/view/news/list"
    response = requests.get(url)
    html_content = response.text

    # BeautifulSoupを使ってHTMLを解析
    soup = BeautifulSoup(html_content, 'html.parser')

    # 現在の日付を取得
    current_date = datetime.now().strftime('%Y.%m.%d')

    # ulタグのクラスがnews-listであるものを取得
    news_list = soup.find('ul', class_='news-list')

    # お知らせのリストを取得
    news_items = news_list.find_all('li')

    # 結果を初期化
    content = None

    # 現在の日時と一致するお知らせを検索
    for item in news_items:
        date_element = item.find('p', class_='news-list-date')
        if date_element and date_element.text.strip() == current_date:
            title_element = item.find('a')
            if title_element and '超ビッグセール' in title_element.text:
                content = "X-PLOSIONで超ビッグセールが開催されています。"
                break

    # メッセージがある場合のみWebhookにPOSTリクエストを送信
    if content:
        response = requests.post(
            os.environ["WEBHOOK_URL"],
            headers={'Content-Type': 'application/json'},
            json={
                "content": content
            }
        )

        # リクエストの結果を確認
        print("Status code:", response.status_code)
        print("Response:", response.text)
    else:
        logger.info("現在の日時と一致するお知らせに「超ビッグセール」は含まれていません。")
