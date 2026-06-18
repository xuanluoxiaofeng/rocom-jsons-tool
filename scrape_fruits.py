import json
import requests
from bs4 import BeautifulSoup
import time

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

if __name__ == '__main__':
    main()
