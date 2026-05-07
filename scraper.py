import os
import json
import base64
import cloudscraper
from bs4 import BeautifulSoup
import re
import time

# بياناتك
GITHUB_TOKEN = "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"
REPO_NAME = "awoadak-glitch/TV"
FILE_PATH = "data.json"
BASE_URL = "https://w1.anime4up.rest"

def get_latest_100_links():
    # استخدام سكرابر أقوى لمحاكاة المتصفح الحقيقي
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome','platform': 'windows','mobile': False})
    all_links = []
    try:
        response = scraper.get(BASE_URL)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # التعديل هنا: البحث عن الروابط داخل الـ "Episodes" في الصفحة الرئيسية
        # موقع Anime4up غالباً يستخدم كلاسات مثل "anime-card-details" أو "ep-card"
        items = soup.select('div.anime-card-container a') or soup.select('div.episodes-card-container a')
        
        for item in items:
            href = item.get('href')
            if href and '/episode/' in href:
                if href not in all_links:
                    all_links.append(href)
            if len(all_links) >= 100: break
            
        print(f"✅ تم العثور على {len(all_links)} رابط لتحديثها.")
        return all_links
    except Exception as e:
        print(f"❌ خطأ في جلب القائمة: {e}")
        return []

def scrape_episode_details(url):
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome','platform': 'windows','mobile': False})
    try:
        res = scraper.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # سحب العنوان
        title_tag = soup.find('h1')
        if not title_tag: return None
        full_title = title_tag.text.strip()
        series_name = re.split(r' الحلقة| Episode', full_title)[0].strip()
        
        # سحب البوستر
        poster = ""
        img = soup.find('img', {'class': 'img-responsive'})
        if img: poster = img.get('src')
        
        # سحب السيرفر
        video_url = ""
        # البحث عن روابط السيرفرات في الـ data-url
        server_link = soup.select_one('ul#episode-servers li a')
        if server_link:
            video_url = server_link.get('data-url') or server_link.get('href')

        if video_url:
            return {
                "series": series_name,
                "ep_name": full_title,
                "poster": poster,
                "url": video_url
            }
    except: return None
    return None

def update_github_database(new_items):
    scraper = cloudscraper.create_scraper()
    api_url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    res = scraper.get(api_url, headers=headers)
    if res.status_code != 200: return
    
    file_info = res.json()
    db = json.loads(base64.b64decode(file_info['content']).decode('utf-8'))

    added = 0
    for data in new_items:
        found = False
        for item in db:
            if item['title'] == data['series']:
                if not any(ep['url'] == data['url'] for ep in item['episodes']):
                    item['episodes'].append({"name": data['ep_name'], "url": data['url']})
                    added += 1
                found = True
                break
        if not found:
            db.append({
                "title": data['series'], "poster": data['poster'],
                "category": "أنمي", "episodes": [{"name": data['ep_name'], "url": data['url']}]
            })
            added += 1

    if added > 0:
        new_content = base64.b64encode(json.dumps(db, indent=2, ensure_ascii=False).encode('utf-8')).decode('utf-8')
        payload = {"message": f"Auto Update: {added} items", "content": new_content, "sha": file_info['sha']}
        scraper.put(api_url, headers=headers, json=payload)
        print(f"🚀 تم إضافة {added} تحديث جديد!")
    else:
        print("😴 لا توجد حلقات جديدة.")

if __name__ == "__main__":
    links = get_latest_100_links()
    final_data = []
    for link in links:
        d = scrape_episode_details(link)
        if d: final_data.append(d)
        time.sleep(0.5)

    if final_data:
        update_github_database(final_data)
