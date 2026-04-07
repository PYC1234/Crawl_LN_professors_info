#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
豆瓣电影Top250爬虫
爬取页面: https://movie.douban.com/top250
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

BASE_URL = "https://movie.douban.com/top250"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://movie.douban.com/",
}


def fetch_page(url, retries=3):
    """获取网页内容"""
    for i in range(retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            resp.encoding = 'utf-8'
            return resp.text
        except requests.RequestException as e:
            print(f"请求失败 (尝试 {i+1}/{retries}): {e}")
            if i < retries - 1:
                time.sleep(2)
    return None


def parse_movie_item(item):
    """解析单个电影信息块"""
    data = {
        "电影名称": None,
        "外文名": None,
        "其他译名": None,
        "导演": None,
        "主演": None,
        "年份": None,
        "国家/地区": None,
        "类型": None,
        "评分": None,
        "评价人数": None,
        "经典短评": None,
        "可播放": None,
        "详情页链接": None,
    }

    # 提取详情页链接和电影名称
    hd = item.find("div", class_="hd")
    if hd:
        first_link = hd.find("a")
        if first_link:
            data["详情页链接"] = first_link.get("href")

            # 提取所有标题文本
            title_spans = first_link.find_all("span", class_="title")
            if title_spans:
                titles = [span.get_text(strip=True) for span in title_spans]
                data["电影名称"] = titles[0] if titles else None
                data["外文名"] = titles[1] if len(titles) > 1 else None

            # 其他译名
            other_spans = first_link.find_all("span", class_="other")
            if other_spans:
                data["其他译名"] = other_spans[0].get_text(strip=True).replace("\xa0", " ")

        # 可播放标记
        playable = hd.find("span", class_="playable")
        if playable:
            data["可播放"] = playable.get_text(strip=True)

    # 提取bd中的详细信息
    bd = item.find("div", class_="bd")
    if bd:
        # 获取所有p标签
        ps = bd.find_all("p")
        if len(ps) >= 1:
            # 第一行: 导演 / 主演 (用 | 分隔，因为<br>在html中是换行)
            line1 = ps[0].get_text(separator="|", strip=True)
            line1 = line1.replace("\xa0", " ")  # 替换非断行空格

            parts1 = [p.strip() for p in line1.split("|")]
            # parts1[0] = "导演: xxx"
            # parts1[1] = "主演: xxx / ..."
            # parts1[2] = "1994 / 美国 / 犯罪 剧情"
            for part in parts1:
                if part.startswith("导演:"):
                    data["导演"] = part.replace("导演:", "").strip()
                elif part.startswith("主演:"):
                    data["主演"] = part.replace("主演:", "").strip()
                elif re.match(r"^\d{4}\s*/", part):
                    # 这是年份/国家/类型行
                    sub_parts = [p.strip() for p in part.split("/")]
                    if len(sub_parts) >= 3:
                        data["年份"] = sub_parts[0].strip()
                        data["国家/地区"] = sub_parts[1].strip()
                        data["类型"] = sub_parts[2].strip()
                    elif len(sub_parts) == 2:
                        data["年份"] = sub_parts[0].strip()
                        data["国家/地区"] = sub_parts[1].strip()

        # 评分和评价人数 (直接在bd下查找)
        rating_num = bd.find("span", class_="rating_num")
        if rating_num:
            data["评分"] = rating_num.get_text(strip=True)

        for span in bd.find_all("span"):
            text = span.get_text(strip=True)
            if "人评价" in text:
                data["评价人数"] = text.replace("人评价", "").strip()

        # 经典短评
        quote = bd.find("p", class_="quote")
        if quote:
            data["经典短评"] = quote.get_text(strip=True).replace("'", "").replace('"', "")

    return data


def parse_top250_page(html):
    """解析豆瓣Top250页面"""
    soup = BeautifulSoup(html, "html.parser")
    movies = []

    # 查找所有电影项
    movie_items = soup.find_all("div", class_="item")
    for item in movie_items:
        movie_data = parse_movie_item(item)
        if movie_data and movie_data["电影名称"]:
            movies.append(movie_data)

    return movies


def crawl_all_pages():
    """爬取所有页面 (共10页，每页25部)"""
    all_movies = []

    for page in range(10):
        if page == 0:
            url = BASE_URL
        else:
            url = f"{BASE_URL}?start={page * 25}"

        print(f"正在爬取第 {page + 1}/10 页: {url}")
        html = fetch_page(url)

        if html:
            movies = parse_top250_page(html)
            all_movies.extend(movies)
            print(f"  -> 获取 {len(movies)} 部电影")
        else:
            print(f"  -> 页面获取失败")

        time.sleep(1)  # 礼貌爬取，避免请求过快

    return all_movies


def save_to_csv(movies, filename="douban_top250.csv"):
    """保存到CSV"""
    df = pd.DataFrame(movies)
    columns = ["电影名称", "外文名", "其他译名", "导演", "主演", "年份",
               "国家/地区", "类型", "评分", "评价人数", "经典短评", "可播放", "详情页链接"]
    df = df.reindex(columns=columns)
    df.to_csv(filename, index=False, encoding="utf-8-sig")
    print(f"已保存到 {filename}")


def save_to_excel(movies, filename="douban_top250.xlsx"):
    """保存到Excel"""
    df = pd.DataFrame(movies)
    columns = ["电影名称", "外文名", "其他译名", "导演", "主演", "年份",
               "国家/地区", "类型", "评分", "评价人数", "经典短评", "可播放", "详情页链接"]
    df = df.reindex(columns=columns)
    df.to_excel(filename, index=False, engine="openpyxl")
    print(f"已保存到 {filename}")


def main():
    print("=" * 50)
    print("豆瓣电影Top250爬虫")
    print("=" * 50)

    movies = crawl_all_pages()

    if movies:
        print(f"\n共获取 {len(movies)} 部电影")

        # 显示前5条预览
        print("\n前5条预览:")
        for i, m in enumerate(movies[:5]):
            print(f"\n{i+1}. {m['电影名称']} ({m['外文名']})")
            print(f"   评分: {m['评分']} | {m['评价人数']}人评价")
            print(f"   {m['年份']} | {m['国家/地区']} | {m['类型']}")
            print(f"   经典短评: {m['经典短评']}")

        save_to_csv(movies)
        save_to_excel(movies)
    else:
        print("未获取到电影信息!")


if __name__ == "__main__":
    main()
