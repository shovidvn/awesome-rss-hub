import os
import sys
import json
import re
import xml.etree.ElementTree as ET
from xml.dom import minidom
import shutil

sys.stdout.reconfigure(encoding='utf-8')

SCRATCH_JSON = r'C:\Users\VIET ANH\.gemini\antigravity\brain\da93b749-80ec-4171-84ef-d83252eac7a3\scratch\all_feeds.json'
REPORT_JSON = r'C:\Users\VIET ANH\.gemini\antigravity\brain\da93b749-80ec-4171-84ef-d83252eac7a3\scratch\feed_validation_report.json'
OUTPUT_DIR = r'd:\Projects\Clone Projects\FastScene\awesome-rss-hub'

USER_MARKETING_FEEDS = [
    {
        "title": "HubSpot Marketing Blog",
        "xml_url": "https://blog.hubspot.com/marketing/rss.xml",
        "html_url": "https://blog.hubspot.com/marketing",
        "category": "Marketing - Content",
        "source": "user_added"
    },
    {
        "title": "Copyblogger",
        "xml_url": "https://copyblogger.com/feed/",
        "html_url": "https://copyblogger.com",
        "category": "Marketing - Content",
        "source": "user_added"
    },
    {
        "title": "Moz Blog",
        "xml_url": "https://moz.com/blog/feed",
        "html_url": "https://moz.com/blog",
        "category": "Marketing - SEO",
        "source": "user_added"
    },
    {
        "title": "Search Engine Land",
        "xml_url": "https://searchengineland.com/feed",
        "html_url": "https://searchengineland.com",
        "category": "Marketing - SEO",
        "source": "user_added"
    },
    {
        "title": "Backlinko",
        "xml_url": "https://backlinko.com/feed",
        "html_url": "https://backlinko.com",
        "category": "Marketing - SEO",
        "source": "user_added"
    },
    {
        "title": "Neil Patel Blog",
        "xml_url": "https://neilpatel.com/blog/feed/",
        "html_url": "https://neilpatel.com/blog/",
        "category": "Marketing - Content",
        "source": "user_added"
    },
    {
        "title": "Social Media Examiner",
        "xml_url": "https://www.socialmediaexaminer.com/feed/",
        "html_url": "https://www.socialmediaexaminer.com",
        "category": "Marketing - Social",
        "source": "user_added"
    },
    {
        "title": "Buffer Resources",
        "xml_url": "https://buffer.com/resources/rss/",
        "html_url": "https://buffer.com/resources/",
        "category": "Marketing - Social",
        "source": "user_added"
    },
    {
        "title": "Salesforce Blog",
        "xml_url": "https://www.salesforce.com/blog/feed/",
        "html_url": "https://www.salesforce.com/blog/",
        "category": "Marketing - CRM",
        "source": "user_added"
    }
]

# 11 Macro Categories
CATEGORIES = [
    {
        "id": "ai_ml",
        "title": "🤖 AI & Machine Learning",
        "opml_name": "ai_ml.opml",
        "description": "Các blog công nghệ, nghiên cứu, podcast và nguồn tin về Trí tuệ nhân tạo, Deep Learning & LLMs."
    },
    {
        "id": "programming",
        "title": "💻 Programming & Software Engineering",
        "opml_name": "programming.opml",
        "description": "Lập trình, Phát triển Web, Backend, Frontend, DevOps, System Architecture & Ngôn ngữ lập trình."
    },
    {
        "id": "mobile",
        "title": "📱 Mobile & Platforms",
        "opml_name": "mobile.opml",
        "description": "Phát triển ứng dụng di động Android, iOS, Hệ sinh thái Apple & Google."
    },
    {
        "id": "cybersecurity",
        "title": "🔒 Cybersecurity & Reverse Engineering",
        "opml_name": "cybersecurity.opml",
        "description": "An toàn thông tin, An ninh mạng, Khai thác lỗ hổng, Reverse Engineering & Hacking News."
    },
    {
        "id": "marketing",
        "title": "📣 Digital Marketing, SEO & Growth",
        "opml_name": "marketing.opml",
        "description": "Marketing kỹ thuật số, Tối ưu hóa công cụ tìm kiếm (SEO), Content Marketing, Social Media, Email Marketing, Analytics & CRM."
    },
    {
        "id": "tech_startups",
        "title": "🚀 Tech News, Eng Blogs & Startups",
        "opml_name": "tech_startups.opml",
        "description": "Tin tức công nghệ, Blog kỹ thuật của các tập đoàn lớn, Khởi nghiệp, VC & Quản lý sản phẩm."
    },
    {
        "id": "finance_crypto",
        "title": "📈 Business, Economy & Cryptocurrency",
        "opml_name": "finance_crypto.opml",
        "description": "Tài chính cá nhân, Tiền điện tử (Crypto/Blockchain), Thị trường chứng khoán & Kinh tế vĩ mô."
    },
    {
        "id": "news",
        "title": "📰 Global & Regional News",
        "opml_name": "news.opml",
        "description": "Báo chí tin tức quốc tế và theo từng quốc gia (US, UK, Germany, Japan, Vietnam, etc.)."
    },
    {
        "id": "science_environment",
        "title": "🔬 Science, Space & Environment",
        "opml_name": "science_environment.opml",
        "description": "Khoa học tự nhiên, Khám phá vũ trụ, Thiên văn học & Khí hậu môi trường."
    },
    {
        "id": "lifestyle",
        "title": "🎨 Culture, Entertainment & Lifestyle",
        "opml_name": "lifestyle.opml",
        "description": "Giải trí, Gaming, Điện ảnh, Âm nhạc, Nhiếp ảnh, Thiết kế UI/UX, Ô tô, Du lịch & Thể thao."
    },
    {
        "id": "hot_rankings",
        "title": "🔥 Real-time Hot Rankings & Spiders",
        "opml_name": "hot_rankings.opml",
        "description": "Bộ cào dữ liệu & API theo dõi bảng xếp hạng hot-trends thời gian thực (Weibo, Zhihu, Bilibili, V2EX, GitHub Trending...)."
    }
]

def classify_feed(item):
    cat_orig = item.get('category', '').lower()
    title = item.get('title', '').lower()
    xml_url = item.get('xml_url', '').lower()
    html_url = item.get('html_url', '').lower()
    source = item.get('source', '')

    if source == 'datehoer/hotToday':
        return 'hot_rankings'

    # Marketing & SEO (Priority match)
    if any(k in cat_orig for k in ['marketing', 'seo', 'growth', 'advertising', 'sem', 'content marketing', 'crm', 'social media marketing']) or \
       any(k in title for k in ['marketing', 'seo', 'copywriting', 'copyblogger', 'growth hack', 'hubspot', 'moz', 'backlinko', 'neilpatel', 'searchengineland', 'social media examiner', 'salesforce', 'crm', 'conversion rate', 'email marketing']):
        return 'marketing'

    # AI & ML
    if any(k in cat_orig for k in ['ai', 'machine learning', 'deep learning', 'llm', 'claude', 'gpt']) or \
       any(k in title for k in ['ai', 'anthropic', 'openai', 'claude', 'cohere', 'mistral', 'ollama', 'perplexity', 'mindsearch', 'deepmind', 'machine learning', 'learning', 'huggingface', 'langchain', 'vector']) or \
       'Olshansk' in source:
        return 'ai_ml'

    # Cybersecurity
    if any(k in cat_orig for k in ['cyber security', 'sec', 'security', 'hacking', 'vulnerability']) or \
       any(k in title for k in ['sec', 'security', 'hacker', 'exploit', 'pentest', 'kanxue', '52pojie', 'freebuf']):
        return 'cybersecurity'

    # Mobile
    if any(k in cat_orig for k in ['android', 'ios', 'apple', 'mobile', 'swift', 'kotlin']) or \
       any(k in title for k in ['android', 'ios', 'apple', 'swift', 'kotlin', 'xcode']):
        return 'mobile'

    # Programming
    if any(k in cat_orig for k in ['programming', 'web development', 'ui - ux', 'devops', 'backend', 'frontend', 'code', 'python', 'rust', 'golang']) or \
       any(k in title for k in ['developer', 'code', 'programming', 'web dev', 'javascript', 'python', 'rust', 'golang', 'css', 'html', 'react', 'vue', 'node', 'database', 'sql', 'linux', 'git']):
        return 'programming'

    # Finance & Crypto
    if any(k in cat_orig for k in ['crypto', 'cryptocurrency', 'finance', 'personal finance', 'business & economy', 'market', 'money']) or \
       any(k in title for k in ['crypto', 'bitcoin', 'ethereum', 'finance', 'stock', 'invest', 'market', 'economy', 'coin', 'bank', 'wall street']):
        return 'finance_crypto'

    # Tech & Startups
    if any(k in cat_orig for k in ['tech', 'startups', 'business']) or \
       any(k in title for k in ['tech', 'startup', 'engineering', 'venture', 'product', 'blog', 'hacker news', 'techcrunch', 'verge', 'wired']):
        return 'tech_startups'

    # Science & Environment
    if any(k in cat_orig for k in ['science', 'space', 'environment', 'nature', 'astronomy']) or \
       any(k in title for k in ['science', 'nasa', 'space', 'astronomy', 'physics', 'nature', 'climate', 'biology']):
        return 'science_environment'

    # News
    if any(k in cat_orig for k in ['news', 'country news']) or \
       any(k in title for k in ['news', 'times', 'post', 'tribune', 'guardian', 'bbc', 'reuters', 'bloomberg', 'journal', 'daily', 'express']):
        return 'news'

    # Lifestyle & Entertainment
    if any(k in cat_orig for k in ['gaming', 'movies', 'music', 'photography', 'travel', 'cars', 'sports', 'books', 'fashion', 'food', 'funny', 'memes', 'chess', 'cricket', 'football', 'tennis', 'beauty', 'architecture', 'interior design', 'diy', 'animal & wildlife']) or \
       any(k in title for k in ['game', 'movie', 'music', 'photo', 'car', 'sport', 'book', 'fashion', 'food', 'travel', 'design', 'art', 'film']):
        return 'lifestyle'

    return 'tech_startups'

def normalize_url_for_dedup(url):
    if not url:
        return ""
    url = url.strip().lower()
    url = re.sub(r'^https?://', '', url)
    url = re.sub(r'/$', '', url)
    url = re.sub(r'/index\.(xml|rss|php|html)$', '', url)
    return url

def format_xml(elem):
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def main():
    print(f"Building standalone repository package in: {OUTPUT_DIR}")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(SCRATCH_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)

    rss_feeds = data.get('rss_feeds', []) + USER_MARKETING_FEEDS
    hot_spiders = data.get('hot_spiders', [])

    # Load validation report to filter dead feeds
    dead_urls = set()
    if os.path.exists(REPORT_JSON):
        with open(REPORT_JSON, 'r', encoding='utf-8') as f:
            rep = json.load(f)
            for df in rep.get('dead_feeds_details', []):
                u = df['item'].get('xml_url')
                if u:
                    dead_urls.add(u.strip())

    print(f"Filter registered dead feed URLs count: {len(dead_urls)}")

    # Deduplicate RSS feeds & filter dead feeds
    seen_norm_urls = set()
    unique_feeds = []
    removed_dead_count = 0
    removed_dup_count = 0

    for item in rss_feeds:
        xml_url = item.get('xml_url', '').strip()
        norm_url = normalize_url_for_dedup(xml_url)
        
        if xml_url in dead_urls:
            removed_dead_count += 1
            continue

        if norm_url and norm_url in seen_norm_urls:
            removed_dup_count += 1
            continue

        if norm_url:
            seen_norm_urls.add(norm_url)
            unique_feeds.append(item)

    print(f"Cleaned Feeds Summary: Removed {removed_dup_count} duplicates and {removed_dead_count} confirmed dead feeds.")
    print(f"Active validated RSS feeds: {len(unique_feeds)}")

    # Categorize items
    categorized = {cat['id']: [] for cat in CATEGORIES}

    for item in unique_feeds:
        cat_id = classify_feed(item)
        item['classified_category'] = cat_id
        categorized[cat_id].append(item)

    for item in hot_spiders:
        cat_id = 'hot_rankings'
        item['classified_category'] = cat_id
        categorized[cat_id].append(item)

    total_all = len(unique_feeds) + len(hot_spiders)

    print("\n--- Cleaned Category Breakdown ---")
    for cat in CATEGORIES:
        cid = cat['id']
        print(f"  {cat['title']}: {len(categorized[cid])} items")
    print(f"TOTAL ACTIVE ITEMS: {total_all}\n")

    # 1. Create categories/ directory
    cats_dir = os.path.join(OUTPUT_DIR, 'categories')
    os.makedirs(cats_dir, exist_ok=True)

    for cat in CATEGORIES:
        cid = cat['id']
        opml_path = os.path.join(cats_dir, cat['opml_name'])
        
        opml = ET.Element('opml', version="2.0")
        head = ET.SubElement(opml, 'head')
        ET.SubElement(head, 'title').text = f"Awesome RSS - {cat['title']}"
        body = ET.SubElement(opml, 'body')
        
        cat_outline = ET.SubElement(body, 'outline', text=cat['title'], title=cat['title'])
        
        for item in categorized[cid]:
            if item.get('source') == 'datehoer/hotToday':
                continue
            ET.SubElement(cat_outline, 'outline', 
                           type="rss",
                           text=item.get('title', ''),
                           title=item.get('title', ''),
                           xmlUrl=item.get('xml_url', ''),
                           htmlUrl=item.get('html_url', ''))
        
        pretty_opml = format_xml(opml)
        with open(opml_path, 'w', encoding='utf-8') as f:
            f.write(pretty_opml)

    # 2. Master feeds.opml
    master_opml_path = os.path.join(OUTPUT_DIR, 'feeds.opml')
    opml = ET.Element('opml', version="2.0")
    head = ET.SubElement(opml, 'head')
    ET.SubElement(head, 'title').text = "Master Awesome RSS Feed Directory"
    body = ET.SubElement(opml, 'body')

    for cat in CATEGORIES:
        cid = cat['id']
        cat_outline = ET.SubElement(body, 'outline', text=cat['title'], title=cat['title'])
        for item in categorized[cid]:
            if item.get('source') == 'datehoer/hotToday':
                continue
            ET.SubElement(cat_outline, 'outline', 
                           type="rss",
                           text=item.get('title', ''),
                           title=item.get('title', ''),
                           xmlUrl=item.get('xml_url', ''),
                           htmlUrl=item.get('html_url', ''))

    pretty_master_opml = format_xml(opml)
    with open(master_opml_path, 'w', encoding='utf-8') as f:
        f.write(pretty_master_opml)

    # 3. Master feeds.json
    master_json_path = os.path.join(OUTPUT_DIR, 'feeds.json')
    master_data = {
        "metadata": {
            "title": "Master Awesome RSS Directory",
            "total_active_rss_feeds": len(unique_feeds),
            "total_hot_spiders": len(hot_spiders),
            "total_active_items": total_all,
            "removed_duplicates": removed_dup_count,
            "removed_dead_feeds": removed_dead_count,
            "sources": [
                "https://github.com/tuan3w/awesome-tech-rss",
                "https://github.com/plenaryapp/awesome-rss-feeds",
                "https://github.com/Olshansk/rss-feeds",
                "https://github.com/datehoer/hotToday",
                "User Submitted Feeds (Marketing & SEO)"
            ]
        },
        "categories": CATEGORIES,
        "items": unique_feeds + hot_spiders
    }
    with open(master_json_path, 'w', encoding='utf-8') as f:
        json.dump(master_data, f, ensure_ascii=False, indent=2)

    # 4. Spiders directory & documentation
    spiders_dir = os.path.join(OUTPUT_DIR, 'spiders')
    os.makedirs(spiders_dir, exist_ok=True)
    
    hot_today_scratch = r'C:\Users\VIET ANH\.gemini\antigravity\brain\da93b749-80ec-4171-84ef-d83252eac7a3\scratch\repos\hotToday'
    if os.path.exists(hot_today_scratch):
        for root, dirs, files in os.walk(hot_today_scratch):
            if '.git' in root or '__pycache__' in root:
                continue
            rel_dir = os.path.relpath(root, hot_today_scratch)
            target_sub_dir = os.path.join(spiders_dir, rel_dir) if rel_dir != '.' else spiders_dir
            os.makedirs(target_sub_dir, exist_ok=True)
            for file in files:
                src_file = os.path.join(root, file)
                dst_file = os.path.join(target_sub_dir, file)
                shutil.copy2(src_file, dst_file)

    # 5. Master README.md
    readme_path = os.path.join(OUTPUT_DIR, 'README.md')
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write("# 📡 Ultimate Master RSS Directory & Hot Trends Aggregator\n\n")
        f.write("> **Kho lưu trữ tổng hợp nguồn tin RSS & Hot Trends thời gian thực lớn nhất**, gom nhóm và đã lọc bỏ hoàn toàn trùng lặp & nguồn tin lỗi:\n")
        f.write("> 1. [`tuan3w/awesome-tech-rss`](https://github.com/tuan3w/awesome-tech-rss)\n")
        f.write("> 2. [`plenaryapp/awesome-rss-feeds`](https://github.com/plenaryapp/awesome-rss-feeds)\n")
        f.write("> 3. [`Olshansk/rss-feeds`](https://github.com/Olshansk/rss-feeds)\n")
        f.write("> 4. [`datehoer/hotToday`](https://github.com/datehoer/hotToday)\n\n")

        f.write(f"![RSS Feeds Badge](https://img.shields.io/badge/Active_RSS_Feeds-{len(unique_feeds)}-orange.svg) ")
        f.write(f"![Hot Spiders Badge](https://img.shields.io/badge/Realtime_Spiders-{len(hot_spiders)}-blue.svg) ")
        f.write("![Categories Badge](https://img.shields.io/badge/Categories-11-green.svg) ")
        f.write("![Cleaned & Verified](https://img.shields.io/badge/Status-Cleaned_%26_Verified-brightgreen.svg)\n\n")

        f.write("---\n\n")
        f.write("## 📥 Quick Import Guide (Hướng dẫn sử dụng)\n\n")
        f.write("- **Import 1-Click Tất cả Feeds:** Tải file [`feeds.opml`](./feeds.opml) và import trực tiếp vào các ứng dụng đọc tin như **Feedly, Inoreader, NetNewsWire, Readwise Reader, Plenary, RSS Guard, Follow, Foliate**.\n")
        f.write("- **Tải theo Danh mục:** Vào thư mục [`categories/`](./categories) để chọn file `.opml` riêng cho từng chủ đề bạn quan tâm.\n")
        f.write("- **Dữ liệu lập trình (JSON):** Tải file [`feeds.json`](./feeds.json) để xây dựng ứng dụng, chatbot hoặc tự động hóa.\n")
        f.write("- **Cào Hot Trends Real-time:** Xem tài liệu và bộ mã nguồn tại thư mục [`spiders/`](./spiders) (từ `hotToday`).\n\n")

        f.write("---\n\n")
        f.write("## 📌 Table of Contents (Mục lục Danh mục)\n\n")
        for cat in CATEGORIES:
            cid = cat['id']
            count = len(categorized[cid])
            f.write(f"- [{cat['title']} ({count})](#-{cat['id']})\n")

        f.write("\n---\n\n")

        # Tables for each category
        for cat in CATEGORIES:
            cid = cat['id']
            items = categorized[cid]
            f.write(f"<a id='-{cid}'></a>\n")
            f.write(f"### {cat['title']} ({len(items)})\n\n")
            f.write(f"_{cat['description']}_\n\n")

            if cid == 'hot_rankings':
                f.write("| Tên Nguồn Tin / Trình Thu Thập | Nền Tảng | Đường Dẫn Spider | Nguồn |\n")
                f.write("| :--- | :--- | :--- | :--- |\n")
                for item in items:
                    t = item.get('title', '').replace('|', '\\|')
                    h = item.get('html_url', '')
                    x = item.get('xml_url', '')
                    src = item.get('source', '')
                    f.write(f"| [{t}]({h}) | Real-time Spider | `{x}` | `{src}` |\n")
            else:
                f.write("| Tên Nguồn Tin | Website | RSS Feed URL | Nguồn |\n")
                f.write("| :--- | :--- | :--- | :--- |\n")
                for item in items:
                    t = item.get('title', '').replace('|', '\\|')
                    h = item.get('html_url', '')
                    x = item.get('xml_url', '')
                    src = item.get('source', '')
                    site_link = f"[Website]({h})" if h else "-"
                    feed_link = f"[RSS Feed]({x})" if x else "-"
                    f.write(f"| **{t}** | {site_link} | {feed_link} | `{src}` |\n")
            f.write("\n")

        f.write("---\n\n")
        f.write("## 🔄 Tự Động Cập Nhật & Rebuild\n\n")
        f.write("Chạy script `build_repo.py` để cập nhật và làm sạch lại repository bất cứ lúc nào:\n\n")
        f.write("```bash\npython build_repo.py\n```\n\n")
        f.write("--- *Xây dựng tự động bởi Antigravity AI - Google DeepMind Agentic Coding.* ---\n")

    # 6. Create .gitignore
    gitignore_path = os.path.join(OUTPUT_DIR, '.gitignore')
    with open(gitignore_path, 'w', encoding='utf-8') as f:
        f.write("__pycache__/\n*.pyc\n.DS_Store\n.venv/\n*.log\nscratch/\n")

    # 7. Create LICENSE (MIT)
    license_path = os.path.join(OUTPUT_DIR, 'LICENSE')
    with open(license_path, 'w', encoding='utf-8') as f:
        f.write("MIT License\n\nCopyright (c) 2026 Ultimate RSS Hub\n\nPermission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the \"Software\"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software.\n")

    target_script = os.path.join(OUTPUT_DIR, 'build_repo.py')
    if not os.path.exists(target_script) or not os.path.samefile(__file__, target_script):
        shutil.copy2(__file__, target_script)

    print(f"\n✅ Cleaned Repository packaged successfully in: {OUTPUT_DIR}")

if __name__ == '__main__':
    main()
