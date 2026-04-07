# 网络爬虫课程实践

本项目包含两个爬虫实战案例，用于课程教学实践。

## 项目结构

```
Crawl_projects/
├── Douban_movies/              # 案例1：豆瓣电影Top250爬虫
│   ├── crawl_douban_top250.py  # 爬虫主程序
│   ├── douban_top250.csv       # 爬取结果（CSV格式）
│   └── requirements.txt        # 依赖包
│
├── LN_proffessors_info/        # 案例2：中山大学岭南学院教授信息爬虫
│   ├── crawl_faculty.py        # 爬虫主程序
│   ├── professors.csv          # 爬取结果（CSV格式）
│   ├── Basis.ipynb             # Jupyter Notebook分析
│   └── requirements.txt        # 依赖包
│
└── README.md
```

## 案例1：豆瓣电影Top250

爬取地址：https://movie.douban.com/top250

### 爬取字段
- 电影名称、外文名、其他译名
- 导演、主演
- 年份、国家/地区、类型
- 评分、评价人数、经典短评
- 可播放标记、详情页链接

### 运行方式
```bash
cd Douban_movies
pip install -r requirements.txt
python crawl_douban_top250.py
```

---

## 案例2：中山大学岭南学院教授信息

爬取地址：https://lingnan.sysu.edu.cn/Faculty

### 爬取字段
- 姓名、职称
- 所属教研室
- 邮箱、研究方向
- 个人主页链接

### 运行方式
```bash
cd LN_proffessors_info
pip install -r requirements.txt
python crawl_faculty.py
```

---

## 通用依赖

```bash
pip install requests beautifulsoup4 pandas openpyxl
```

## 注意事项

1. 请遵守网站的robots.txt和使用条款
2. 爬取时设置适当的请求间隔，避免对服务器造成压力
3. 妥善保管爬取的数据，不要用于商业用途
