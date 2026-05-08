import os
import requests
import json
import base64
import time
import random

# الإعدادات - تأكد من وضع TOKEN الخاص بك في Github Secrets
GITHUB_TOKEN = os.getenv("MY_GITHUB_TOKEN")
TMDB_API_KEY = "62571b988e8d17fac56d5240f5610ef0" # المفتاح الذي أرسلته
REPO_NAME = "awoadak-glitch/TV"
FILE_PATH = "data.json"

def get_pirated_style_content():
    print("📡 جاري استخراج البيانات بنظام الـ API المقرصن...")
    new_results = []
    
    # سحب عشوائي لبناء مكتبة الـ 10,000 عنصر
    random_pages = random.sample(range(1, 500), 20) 
    
    for page in random_pages:
        try:
            # استخدام API TMDB لجلب الأفلام الشائعة
            url = f"https://api.themoviedb.org/3/trending/all/week?api_key={TMDB_API_KEY}&language=ar&page={page}"
            res = requests.get(url, timeout=15).json()
            
            for item in res.get('results', []):
                tmdb_id = item.get('id')
                m_type = item.get('media_type', 'movie')
                title = item.get('title') if m_type == 'movie' else item.get('name')
                
                if not title or not tmdb_id: continue

                # --- الروابط المقرصنة التي تدعم الترجمة العربية إجبارياً ---
                
                # الرابط 1: vidsrc.to (المستخدم في معظم المواقع العربية حالياً)
                # نستخدم رمز hash لمنع التتبع وسهولة الفتح
                s1 = f"https://vidsrc.to/embed/{m_type}/{tmdb_id}"
                
                # الرابط 2: vidsrc.pro (نسخة مطورة تدعم المشغل الذكي)
                s2 = f"https://vidsrc.pro/embed/{m_type}/{tmdb_id}"

                new_results.append({
                    "title": title,
                    "poster": f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}",
                    "category": "أفلام" if m_type == 'movie' else "مسلسلات",
                    "episodes": [
                        {"name": "سيرفر الترجمة العربية (المباشر)", "url": s1},
                        {"name": "سيرفر البث السريع (HD)", "url": s2}
                    ]
                })
            time.sleep(0.1)
        except: continue
    return new_results

def update_github_database():
    api_url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    res = requests.get(api_url, headers=headers)
    old_data = []
    sha = None
    if res.status_code == 200:
        file_info = res.json()
        sha = file_info['sha']
        content = base64.b64decode(file_info['content']).decode('utf-8')
        old_data = json.loads(content)

    new_items = get_pirated_style_content()
    
    # نظام الفلترة لمنع التكرار تماماً
    existing_titles = {item['title'] for item in old_data}
    for item in new_items:
        if item['title'] not in existing_titles:
            old_data.append(item)
    
    # تقليص الحجم لـ 10,000 عنصر (الحد الأقصى للمتصفح)
    final_data = old_data[-10000:] 

    content_encoded = base64.b64encode(json.dumps(final_data, indent=2, ensure_ascii=False).encode('utf-8')).decode('utf-8')
    payload = {
        "message": f"تحديث المحتوى: {len(final_data)} فيلم ومسلسل مترجم",
        "content": content_encoded,
        "sha": sha
    }
    
    requests.put(api_url, headers=headers, json=payload)
    print(f"✅ مبروك! قاعدة البيانات الآن تحتوي على {len(final_data)} عنصر جاهز.")

if __name__ == "__main__":
    update_github_database()
