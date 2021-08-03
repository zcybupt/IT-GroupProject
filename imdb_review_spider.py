import json
import re
import time

import requests
from lxml import etree
from imdb import IMDb
from requests import Response

top_250_list = [
    '0111161', '0068646', '0071562', '0468569', '0050083', '0108052', '0167260', '0110912', '0060196', '0120737',
    '0137523', '0109830', '1375666', '0167261', '0080684', '0133093', '0099685', '0073486', '0047478', '0114369',
    '0102926', '0317248', '0118799', '0038650', '0076759', '0120815', '0245429', '0816692', '0120689', '6751668',
    '0110413', '0056058', '0114814', '0253474', '0088763', '0103064', '0027977', '0054215', '0110357', '0120586',
    '0021749', '0095327', '0172495', '2582802', '0407887', '1675434', '0482571', '0034583', '0064116', '0047396',
    '0095765', '0078748', '0078788', '0209144', '0082971', '0032553', '0405094', '1853728', '0050825', '0043014',
    '0910970', '0081505', '4154756', '0051201', '0057012', '7286456', '4633694', '0364569', '0119698', '5311514',
    '8503618', '0087843', '1345836', '0090605', '2380307', '0082096', '8267604', '4154796', '0057565', '0169547',
    '0114709', '1187043', '0112573', '0086879', '0361748', '0048473', '0119217', '0086190', '0062622', '0105236',
    '0986264', '0022100', '0052357', '0033467', '2106476', '0091251', '0180093', '0045152', '0053125', '0338013',
    '0044741', '0040522', '0056172', '0012349', '5074352', '0093058', '10272386', '0066921', '0017136', '0075314',
    '0053604', '1255953', '0036775', '0070735', '8579674', '1832382', '0211915', '0208092', '0086250', '0435761',
    '0056592', '0059578', '1049413', '0097576', '0119488', '0113277', '0042876', '0055630', '0089881', '0095016',
    '6966692', '0071853', '0363163', '0042192', '0053291', '0372784', '0105695', '0118849', '0347149', '0993846',
    '0057115', '0055031', '0112641', '0040897', '0469494', '0457430', '0268978', '1305806', '0081398', '0096283',
    '0071315', '0120735', '0015864', '1130884', '0477348', '0046912', '5027774', '0050976', '0080678', '0084787',
    '0167404', '4729430', '2096673', '0434409', '0041959', '0050986', '0083658', '0353969', '0120382', '0117951',
    '0107290', '0050212', '1291584', '0116282', '0476735', '0266543', '0031381', '0266697', '0046438', '0047296',
    '0079944', '0017925', '3011894', '0015324', '0077416', '1205489', '2278388', '0060827', '0112471', '3170832',
    '0978762', '1392214', '0031679', '0107207', '0264464', '2267998', '0035446', '2119532', '8108198', '0072684',
    '0019254', '0118715', '1950186', '2024544', '0892769', '1392190', '0052618', '0097165', '0405159', '0046268',
    '0077711', '0074958', '1201607', '0092005', '4016934', '0061512', '0053198', '3315342', '0116231', '1028532',
    '0091763', '0113247', '1895587', '1954470', '0079470', '0395169', '0198781', '0032976', '1979320', '0060107',
    '0758758', '5323662', '0245712', '0118694', '0075148', '0025316', '0087544', '0058946', '0381681', '7060344',
    '0169858', '0083922', '0111495', '0048021', '0093779', '0018455', '0242519', '3417422', '0050783', '0087884'
]

review_url = 'https://www.imdb.com/title/tt%s/reviews'

proxy = 'http://127.0.0.1:7890'

proxies = {'http': proxy, 'https': proxy}

i = IMDb()
i.set_proxy(proxy)


def get_resource_with_retry(imdb_id: str, times: int = 3) -> Response:
    if times == 0:
        res = Response()
        res.status_code = 500
        return res

    try:
        res = requests.get(review_url % imdb_id, proxies=proxies)
        return res
    except Exception:
        print('Failed to retrieve %s. Retry after 5s' % imdb_id)
        time.sleep(5)
        return get_resource_with_retry(imdb_id, times - 1)


def get_review_dict(imdb_id: str) -> dict:
    res = get_resource_with_retry(imdb_id)
    if not res or res.status_code != 200:
        print('Failed to retrieve review: %s.' % imdb_id)
        return

    root = etree.HTML(res.text)
    review_container_list = root.xpath('//div[@class="review-container"]')
    for review_container in review_container_list:
        rating = review_container.xpath('.//span[@class="rating-other-user-rating"]/span[1]/text()')
        rating = int(rating[0]) if rating else -1
        _, user, review_time, _ = review_container.xpath('.//div[@class="display-name-date"]//text()')
        title = review_container.xpath('.//a[@class="title"]/text()')[0].strip()
        content = review_container.xpath('.//div[@class="content"]/div[1]/text()')
        content = '\n'.join(content) if len(content) > 1 else content
        likes_text = review_container.xpath('.//div[@class="content"]/div[2]/text()')[0].strip()
        likes, _ = re.findall('[\d,]+', likes_text)

        review_dict = {
            'imdb_id': imdb_id,
            'user': user,
            'title': title,
            'content': content,
            'time': review_time,
            'likes': int(likes.replace(',', '')),
            'rating': rating
        }

        yield review_dict


def get_movie_info(imdb_id: str, times: int = 3) -> dict:
    if times == 0:
        print('Failed to get movie info: %s' % imdb_id)
        return {}

    movie = i.get_movie(imdb_id)
    if not movie:
        print('Failed to retrieve movie info: %s. Retry after 5s' % imdb_id)
        return get_movie_info(imdb_id, times - 1)

    genres = movie.get('genres')
    name = movie.get('title')
    description = movie.get('plot outline')
    pic_url = movie.get('cover url')
    actual_pic_url = re.findall('(.*@).*', pic_url)
    pic_url = actual_pic_url[0] if actual_pic_url else pic_url
    release_year = movie.get('year')
    rating = movie.get('rating')

    movie_dict = {
        'imdb_id': imdb_id,
        'genres': genres,
        'name': name,
        'description': description,
        'pic_url': pic_url,
        'release_year': release_year,
        'rating': rating,
    }

    return movie_dict


def save_reviews_as_json() -> None:
    with open('imdb_top250.json', 'w') as f:
        for imdb_id in top_250_list:
            movie = get_movie_info(imdb_id)
            if not movie: continue
            print('current id: %s\t%s' % (imdb_id, movie.get('name')))

            review_list = []
            for review in get_review_dict(imdb_id):
                review_list.append(review)

            movie['reviews'] = review_list
            json_str = json.dumps(movie)
            f.write(json_str + '\n')


if __name__ == '__main__':
    save_reviews_as_json()
