import os
import json
import base64
import cloudscraper
from bs4 import BeautifulSoup
import re

# بياناتك مدمجة مباشرة
GITHUB_TOKEN = "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"
REPO_NAME = "awoadak-glitch/TV"
FILE_PATH = "data.json"

def get_video_data(url, category):
    # إنشاء متصفح يتجاوز Cloudflare
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})
    try:
        response = scraper.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. استخراج اسم الحلقة والأنمي
        title_raw = soup.find('h1').text.strip() if soup.find('h1') else "Unknown"
        # تنظيف الاسم: ون بيس الحلقة 1 -> ون بيس
        series_name = re.split(r' الحلقة| Episode', title_raw)[0].strip()
        
        # 2. استخراج البوستر (صورة الأنمي)
        poster = ""
        img_tag = soup.find('img', {'class': 'img-responsive'})
        if img_tag:
            poster = img_tag.get('src')
        
        # 3. استخراج رابط سيرفر المشاهدة
        video_url = ""
        # البحث في قائمة السيرفرات (عن سيرفر 4up أو السيرفر الرئيسي)
        servers_list = soup.find('ul', {'id': 'episode-servers'})
        if servers_list:
            links = servers_list.find_all('a')
            for link in links:
                # نفضل السيرفرات التي تحتوي على رابط مباشر في data-url
                temp_url = link.get('data-url')
                if temp_url and 'http' in temp_url:
                    video_url = temp_url
                    break
        
        # إذا لم ينجح، نبحث عن أول iframe في الصفحة
        if not video_url:
            iframe = soup.find('iframe')
            if iframe:
                video_url = iframe.get('src')

        if not video_url:
            print("تحذير: لم يتم العثور على رابط فيديو، قد يحتاج الموقع لتحديث منطق السحب.")

        return {
            "series": series_name,
            "ep_name": title_raw,
            "poster": poster,
            "url": video_url,
            "category": category
        }
    except Exception as e:
        print(f"حدث خطأ أثناء السحب: {e}")
        return None

def update_db(data):
    scraper = cloudscraper.create_scraper()
    api_url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # جلب data.json الحالي
    res = scraper.get(api_url, headers=headers)
    if res.status_code != 200:
        print(f"خطأ في الوصول للمستودع: {res.status_code}")
        return

    file_info = res.json()
    content = base64.b64decode(file_info['content']).decode('utf-8')
    db = json.loads(content)

    # البحث عن الأنمي لتحديثه أو إضافته
    found = False
    for item in db:
        if item['title'] == data['series']:
            # إضافة الحلقة للمجموعة إذا لم تكن موجودة مسبقاً
            if not any(ep['url'] == data['url'] for ep in item.get('episodes', [])):
                if 'episodes' not in item: item['episodes'] = []
                item['episodes'].append({"name": data['ep_name'], "url": data['url']})
            found = True
            break
    
    if not found:
        db.append({
            "title": data['series'],
            "poster": data['poster'],
            "category": data['category'],
            "episodes": [{"name": data['ep_name'], "url": data['url']}]
        })

    # رفع التحديث إلى GitHub
    updated_json = json.dumps(db, indent=2, ensure_ascii=False)
    new_content_b64 = base64.b64encode(updated_json.encode('utf-8')).decode('utf-8')
    
    payload = {
        "message": f"إضافة حلقة: {data['ep_name']}",
        "content": new_content_b64,
        "sha": file_info['sha']
    }
    
    put_res = scraper.put(api_url, headers=headers, json=payload)
    if put_res.status_code == 200:
        print(f"✅ نجحت العملية: تم إضافة {data['ep_name']} إلى المكتبة.")
    else:
        print(f"❌ فشل الرفع: {put_res.text}")

if __name__ == "__main__":
    event_path = os.getenv('GITHUB_EVENT_PATH')
    if event_path:
        with open(event_path, 'r') as f:
            event_data = json.load(f)
            inputs = event_data.get('inputs', {})
            target = inputs.get('target_url')
            cat = inputs.get('category', 'أنمي')
            
            if target:
                result = get_video_data(target, cat)
                if result:
                    update_db(result)
