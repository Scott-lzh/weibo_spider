from urllib.parse import urlencode

from pymongo import MongoClient
from pyquery import PyQuery as pq
import requests
import json

base_url = 'https://m.weibo.cn/api/container/getIndex?'
headers = {
    'Host': 'm.weibo.cn',
    'Referer': 'https://m.weibo.cn/u/2830678474',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
}


def get_page(since_id, page):
    params = {
        'uid': '2830678474',
        'display': '0',
        'retcode': '6102',
        'type': 'uid',
        'value': '2830678474',
        'containerid': '1076032830678474',
    }
    if (page > 1):
        params['since_id'] = since_id
    url = base_url + urlencode(params)
    print(url)
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.ConnectionError as e:
        print('Error', e.args)


def parse_page(json):
    if json:
        items = json.get('data').get('cards')
        for item in items:
            item = item.get('mblog')
            weibo = {}
            weibo['id'] = item.get('id')
            weibo['text'] = pq(item.get('text')).text()
            weibo['attitudes'] = item.get('attitudes_count')
            weibo['comments'] = item.get('comments_count')
            weibo['reposts'] = item.get('reposts_count')
            yield weibo


if __name__ == '__main__':
    page = 1
    since_id = 1
    while page <= 10:
        html = get_page(since_id, page)
        since_id = html.get('data').get('cardlistInfo').get('since_id')
        results = parse_page(html)
        for result in results:
            print(result)

            # client = MongoClient()
            # db = client['weibo']
            # collection = db['weibo']
            # if collection.insert(result):
            #     print('Saved to Mongo')
            file = open('weibo.txt', 'a', encoding='utf-8')
            text = result.get('text')
            if len(text) > 0:
                file.write(text)
                file.write('\n')
            # file.write(json.dumps(result, indent=2, ensure_ascii=False))
        file.write('=' * 50 + '\n')
        file.close()
        page = page + 1
