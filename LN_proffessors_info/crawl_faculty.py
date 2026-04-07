#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中山大学岭南学院教授信息爬虫
爬取页面: https://lingnan.sysu.edu.cn/Faculty
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
from urllib.parse import urljoin

# 配置
BASE_URL = "https://lingnan.sysu.edu.cn"
FACULTY_URL = "https://lingnan.sysu.edu.cn/Faculty"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
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


def parse_faculty_item(html_block):
    """解析单个教授信息块"""
    data = {
        "姓名": None,
        "职称": None,
        "所属教研室": None,
        "邮箱": None,
        "研究方向": None,
        "个人主页链接": None,
    }

    soup = BeautifulSoup(html_block, "html.parser")

    # 提取姓名和链接 (在 h3 > a 中)
    name_tag = soup.find("h3")
    if name_tag:
        a_tag = name_tag.find("a")
        if a_tag:
            data["姓名"] = a_tag.get_text(strip=True)
            href = a_tag.get("href", "")
            if href:
                data["个人主页链接"] = urljoin(BASE_URL, href)

        # 提取职称 (在 h3 > span 中)
        span_tag = name_tag.find("span")
        if span_tag:
            data["职称"] = span_tag.get_text(strip=True)

    # 提取其他字段 (在 p 标签中)
    for p in soup.find_all("p"):
        text = p.get_text(strip=True)
        class_attr = p.get("class", [])

        if "one-line" in class_attr:
            # 可能是教研室或邮箱
            if "@" in text and "邮箱" not in text:
                data["邮箱"] = text
            elif "教研室" in text or "系" in text:
                data["所属教研室"] = text
        elif "two-line" in class_attr or "text-light" in class_attr:
            # 研究方向
            if "研究方向" in text:
                research = text.replace("研究方向:", "").replace("研究方向:", "").strip()
                data["研究方向"] = research

    return data


def parse_faculty_page(html):
    """解析 Faculty 主页，提取所有教授信息"""
    soup = BeautifulSoup(html, "html.parser")
    professors = []

    # 查找所有教授信息块
    # 根据示例HTML结构: div.infors
    info_blocks = soup.find_all("div", class_="infors")

    for block in info_blocks:
        prof_data = parse_faculty_item(str(block))
        if prof_data and prof_data["姓名"]:
            professors.append(prof_data)

    return professors


def crawl_all_faculty():
    """爬取所有教授信息"""
    print(f"正在爬取: {FACULTY_URL}")

    html = fetch_page(FACULTY_URL)
    if not html:
        print("获取页面失败!")
        return []

    print("正在解析页面...")
    professors = parse_faculty_page(html)

    print(f"共找到 {len(professors)} 位教授")
    return professors


def save_to_csv(professors, filename="professors.csv"):
    """保存到CSV文件"""
    df = pd.DataFrame(professors)
    # 重新排列列顺序
    columns = ["姓名", "职称", "所属教研室", "邮箱", "研究方向", "个人主页链接"]
    df = df.reindex(columns=columns)
    df.to_csv(filename, index=False, encoding="utf-8-sig")
    print(f"已保存到 {filename}")


def save_to_excel(professors, filename="professors.xlsx"):
    """保存到Excel文件"""
    df = pd.DataFrame(professors)
    columns = ["姓名", "职称", "所属教研室", "邮箱", "研究方向", "个人主页链接"]
    df = df.reindex(columns=columns)
    df.to_excel(filename, index=False, engine="openpyxl")
    print(f"已保存到 {filename}")


def main():
    print("=" * 50)
    print("中山大学岭南学院教授信息爬虫")
    print("=" * 50)

    professors = crawl_all_faculty()

    if professors:
        # 显示前几条数据
        print("\n前5条数据预览:")
        for i, p in enumerate(professors[:5]):
            print(f"\n{i+1}. {p['姓名']} | {p['职称']} | {p['所属教研室']}")
            print(f"   邮箱: {p['邮箱']}")
            print(f"   研究方向: {p['研究方向']}")

        # 保存结果
        save_to_csv(professors)
        save_to_excel(professors)
    else:
        print("未找到教授信息!")


if __name__ == "__main__":
    main()
