import json
import requests
from bs4 import BeautifulSoup
import time
import re
import random
import string
from datetime import datetime, timedelta, timezone
from pathlib import Path

def get_soup_from_url(url):
    """
    从网络URL获取网页内容并返回 BeautifulSoup 对象
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response.encoding = 'utf-8'
        return BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"错误：下载网页 {url} 时出现问题 - {e}")
        return None

def scrape_fruits():
    """
    爬取精灵果实图鉴数据
    """
    url = "https://wiki.biligame.com/rocom/精灵果实图鉴"
    print(f"正在抓取果实数据: {url}")
    soup = get_soup_from_url(url)
    if not soup:
        return []

    fruits_data = []
    # 根据网页结构，果实信息在 class 为 'divsort' 的 div 中
    fruit_divs = soup.find_all('div', class_='divsort')

    for div in fruit_divs:
        # 提取名称
        name_tag = div.find('p', class_='rocom_prop_name')
        name = name_tag.find('a').text.strip() if name_tag and name_tag.find('a') else None
        
        # 提取图片链接
        img_tag = div.find('img', class_='rocom_prop_icon')
        # 处理相对链接
        image_url = img_tag.get('src') if img_tag else None
        if image_url and image_url.startswith('/'):
            image_url = "https://wiki.biligame.com" + image_url

        if name and image_url:
            fruits_data.append({
                "name": name,
                "image_url": image_url
            })
    
    print(f"果实数据抓取完成，共 {len(fruits_data)} 条。")
    return fruits_data

def scrape_pokemon():
    """
    爬取精灵图鉴数据
    """
    url = "https://wiki.biligame.com/rocom/%E7%B2%BE%E7%81%B5%E5%9B%BE%E9%89%B4"
    print(f"正在抓取精灵数据: {url}")
    soup = get_soup_from_url(url)
    
    if not soup:
        return []

    pokemon_data = []

    # 核心修复：通过查找所有带有 data-param1 属性的 div 来定位精灵卡片
    # 这是精灵卡片独有的特征，非常稳健
    pet_cards = soup.find_all('div', attrs={"data-param1": True})
    
    print(f"共找到 {len(pet_cards)} 个精灵卡片。")

    for card in pet_cards:
        # 1. 提取编号和阶数
        # 编号和阶数在 class 为 'dex-card-kicker' 的 div 中
        kicker_div = card.find('div', class_='dex-card-kicker')
        if not kicker_div:
            continue

        # HTML 结构里编号和阶数被分成文本和 <span>，用 separator=' ' 将它们分开
        kicker_text = kicker_div.get_text(separator=' ', strip=True)
        parts = kicker_text.split(' ')
        if len(parts) < 2:
            continue
        pokedex_id = parts[0].replace('NO.', '')
        rank_info = parts[1]

        # 2. 提取名称
        # 名称在 class 为 'dex-card-name' 的 div 中的 <a> 标签里
        name_container = card.find('div', class_='dex-card-name')
        name_tag = name_container.find('a') if name_container else None
        name = name_tag.text.strip() if name_tag else None
        if not name:
            continue

        # 3. 提取图片链接
        # 图片在 class 为 'dex-pet-art' 的 div 中的 <img> 标签里
        # 注意：异色精灵有两个 img，我们取第一个（原始形态）
        img_tag = card.find('div', class_='dex-pet-art').find('img')
        image_url = img_tag.get('src') if img_tag else None
        if not image_url:
            continue
        # 处理相对链接
        if image_url.startswith('/'):
            image_url = "https://wiki.biligame.com" + image_url

        pokemon_data.append({
            "id": pokedex_id,
            "name": name,
            "rank": rank_info,
            "image_url": image_url
        })

    print(f"精灵数据解析完成，共 {len(pokemon_data)} 条。")
    return pokemon_data

API_URL = 'https://rocokingdomworld.org/api/merchant/live'
LIVE_FILE = Path(__file__).parent / 'live.json'
RAW_FILE = Path(__file__).parent / 'raw.json'

ROUND_SCHEDULE = {
    1: {'start': '08:00:00', 'end': '11:55:00'},
    2: {'start': '12:00:00', 'end': '15:55:00'},
    3: {'start': '16:00:00', 'end': '19:55:00'},
    4: {'start': '20:00:00', 'end': '23:55:00'}
}

def generate_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=16)) + ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))

def compute_round_times(date_str):
    times = {}
    tz = timezone(timedelta(hours=8))
    for round_num in [1, 2, 3, 4]:
        schedule = ROUND_SCHEDULE[round_num]
        start_time_str = f"{date_str}T{schedule['start']}"
        end_time_str = f"{date_str}T{schedule['end']}"
        
        start_time = int(datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=tz).timestamp() * 1000)
        end_time = int(datetime.strptime(end_time_str, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=tz).timestamp() * 1000)
        
        times[round_num] = {
            'start_time': start_time,
            'end_time': end_time
        }
    return times

def transform_to_raw_format(live_data):
    date_str = ''
    if live_data.get('startedAtBeijing'):
        date_str = live_data['startedAtBeijing'].split(' ')[0]
    elif live_data.get('nextRefreshBeijing'):
        date_str = live_data['nextRefreshBeijing'].split(' ')[0]
    else:
        now = datetime.now()
        date_str = now.strftime('%Y-%m-%d')
    
    round_times = compute_round_times(date_str)
    
    get_props = []
    random_goods = []
    
    for round_num in [1, 2, 3, 4]:
        items = live_data.get('rounds', {}).get(str(round_num), [])
        times = round_times[round_num]
        
        for item in items:
            get_props.append({
                '_id': generate_id(),
                'end_time': times['end_time'],
                'icon_url': item.get('image', ''),
                'name': item.get('name', ''),
                'start_time': times['start_time']
            })
    
    item_id_map = {}
    id_counter = 100001
    
    for item in live_data.get('items', []):
        price = int(item.get('price', '0'))
        buy_limit = int(item.get('limit', '1'))
        
        item_id = ''
        img_match = re.search(r'(\d+)\.png', item.get('image', ''))
        if img_match:
            item_id = img_match.group(1)
        
        item_id_map[item.get('name', '')] = item_id
        
        random_goods.append({
            'Type': 1,
            'buy_limit_num': buy_limit,
            'enable': True,
            'goods_name': item.get('name', ''),
            'id': id_counter,
            'item_id': int(item_id) if item_id else 0,
            'item_num': 1,
            'origin_price': price,
            'price': price,
            'price_goods_id': 1,
            'price_goods_type': 2,
            'weight': 1
        })
        id_counter += 1
    
    return {
        'code': 0,
        'message': '成功',
        'data': {
            'merchantActivities': [{
                '_id': generate_id(),
                'cover_url': '',
                'created_at': int(time.time() * 1000),
                'created_by': generate_id(),
                'description': '',
                'end_time': round_times[4]['end_time'],
                'get_extra_props': [],
                'get_pets': [],
                'get_props': get_props,
                'is_deleted': False,
                'is_public': True,
                'is_unlimited': False,
                'name': '远行商人',
                'sort': 0,
                'start_date': date_str,
                'start_time': round_times[1]['start_time']
            }],
            'random_goods': random_goods
        }
    }

def download_and_transform():
    print('正在从 API 下载数据...')
    
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        live_data = response.json()
        
        with open(LIVE_FILE, 'w', encoding='utf-8') as f:
            json.dump(live_data, f, ensure_ascii=False, indent=2)
        print(f'原始数据已保存到 {LIVE_FILE}')
        
        raw_data = transform_to_raw_format(live_data)
        with open(RAW_FILE, 'w', encoding='utf-8') as f:
            json.dump(raw_data, f, ensure_ascii=False, indent=2)
        print(f'转换后数据已保存到 {RAW_FILE}')
        
        print('\n=== 转换结果 ===')
        print(f"商人活动: {len(raw_data['data']['merchantActivities'])} 个")
        print(f"物品属性: {len(raw_data['data']['merchantActivities'][0]['get_props'])} 个")
        print(f"随机商品: {len(raw_data['data']['random_goods'])} 个")
        start_time = datetime.fromtimestamp(raw_data['data']['merchantActivities'][0]['start_time'] / 1000, tz=timezone(timedelta(hours=8)))
        end_time = datetime.fromtimestamp(raw_data['data']['merchantActivities'][0]['end_time'] / 1000, tz=timezone(timedelta(hours=8)))
        print(f"开始时间: {start_time.strftime('%Y/%m/%d %H:%M:%S')}")
        print(f"结束时间: {end_time.strftime('%Y/%m/%d %H:%M:%S')}")
        
    except Exception as e:
        print(f'处理失败: {e}')

def main():
    # 1. 抓取果实数据
    fruits = scrape_fruits()
    if fruits:
        with open('fruits.json', 'w', encoding='utf-8') as f:
            json.dump(fruits, f, ensure_ascii=False, indent=2)
        print("果实数据已保存到 fruits.json")
    
    # 2. 抓取精灵数据
    # 为了避免对服务器造成压力，增加一点延迟
    time.sleep(1)
    pokemon = scrape_pokemon()
    if pokemon:
        with open('pokemon.json', 'w', encoding='utf-8') as f:
            json.dump(pokemon, f, ensure_ascii=False, indent=2)
        print("精灵数据已保存到 pokemon.json")
    
    # 3. 下载并转换商人数据
    time.sleep(1)
    download_and_transform()

if __name__ == '__main__':
    main()
