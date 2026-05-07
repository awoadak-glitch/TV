import os
import json
import base64
import cloudscraper
from bs4 import BeautifulSoup
import re
import time

# بيانات الوصول الخاصة بك
GITHUB_TOKEN = "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"
REPO_NAME = "awoadak-glitch/TV"
FILE_PATH = "data.json"
BASE_URL = "https://w1.anime4up.rest"

def get_latest_100_links():
    scraper = cloudscraper.create_scraper()
    all_links = []
    # الموقع يعرض عدداً معيناً في الصفحة الرئيسية، سنحاول جمع أول 100 رابط
    try:
        response = scraper.get(BASE_URL)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # البحث عن روابط الحلقات في الصفحة الرئيسية
        items = soup.find_all('div', {'class': 'anime-card-container'})
        for item in items:
            link_tag = item.find('a')
            if link_tag:
                all_links.append(link_tag['href'])
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
        
        # اسم الحلقة الكامل
        full_title = soup.find('h1').text.strip()
        # استخراج اسم الأنمي فقط
        series_name = re.split(r' الحلقة| Episode', full_title)[0].strip()
        
        # البوستر
        img = soup.find('img', {'class': 'img-responsive'})
        poster = img['src'] if img else ""
        
        # رابط سيرفر المشاهدة
        video_url = ""
        server_list = soup.find('ul', {'id': 'episode-servers'})
        if server_list:
            first_link = server_list.find('a')
            video_url = first_link.get('data-url') or first_link.get('href')

        if video_url:
            return {
                "series": series_name,
                "ep_name": full_title,
                "poster": poster,
                "url": video_url
            }
    except:
        return None
    return None

def update_github_database(new_items):
    scraper = cloudscraper.create_scraper()
    api_url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}

    # جلب الداتا الحالية
    res = scraper.get(api_url, headers=headers)
    if res.status_code != 200: return
    
    file_info = res.json()
    db = json.loads(base64.b64decode(file_info['content']).decode('utf-8'))

    updates_count = 0
    for data in new_items:
        found = False
        for item in db:
            if item['title'] == data['series']:
                # إذا الأنمي موجود، أضف الحلقة فقط إذا لم تكن موجودة
                if not any(ep['url'] == data['url'] for ep in item['episodes']):
                    item['episodes'].append({"name": data['ep_name'], "url": data['url']})
                    updates_count += 1
                found = True
                break
        
        if not found:
            # إذا أنمي جديد تماماً، أضفه للمكتبة
            db.append({
                "title": data['series'],
                "poster": data['poster'],
                "category": "أنمي",
                "episodes": [{"name": data['ep_name'], "url": data['url']}]
            })
            updates_count += 1

    if updates_count > 0:
        # رفع التحديثات
        updated_json = json.dumps(db, indent=2, ensure_ascii=False)
        payload = {
            "message": f"Auto-update: Added/Updated {updates_count} items",
            "content": base64.b64encode(updated_json.encode('utf-8')).decode('utf-8'),
            "sha": file_info['sha']
        }
        scraper.put(api_url, headers=headers, json=payload)
        print(f"🚀 تم تحديث المكتبة بـ {updates_count} عنصر جديد.")
    else:
        print("😴 لا توجد تحديثات جديدة لإضافتها.")

if __name__ == "__main__":
    links = get_latest_100_links()
    final_data = []
    
    for i, link in enumerate(links):
        print(f"جاري معالجة ({i+1}/100): {link}")
        details = scrape_episode_details(link)
        if details:
            final_data.append(details)
        time.sleep(1) # تأخير بسيط لتجنب الحظر

    if final_data:
        update_github_database(final_data)
