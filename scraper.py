import os
import requests
import json
import base64
import time
import random

# الإعدادات
GITHUB_TOKEN = os.getenv("MY_GITHUB_TOKEN")
TMDB_API_KEY = "62571b988e8d17fac56d5240f5610ef0"
REPO_NAME = "awoadak-glitch/TV"
FILE_PATH = "data.json"

def get_extensive_content():
    print("🎬 جاري سحب محتوى جديد بروابط 2Embed المصححة...")
    new_results = []
    
    # اختيار صفحات عشوائية لضمان التنوع
    random_pages = random.sample(range(1, 100), 10) 
    
    for page in random_pages:
        try:
            # نسحب مزيجاً من الأفلام والمسلسلات
            url = f"https://api.themoviedb.org/3/trending/all/week?api_key={TMDB_API_KEY}&language=ar&page={page}"
            res = requests.get(url, timeout=15).json()
            
            for item in res.get('results', []):
                tmdb_id = item.get('id')
                m_type = item.get('media_type', 'movie')
                title = item.get('title') if m_type == 'movie' else item.get('name')
                
                if not title or not tmdb_id: continue

                # --- التصحيح الحاسم لروابط 2Embed ---
                # للأفلام: يجب أن يكون المسار /embedmovie/ID
                if m_type == 'movie':
                    watch_url = f"https://www.2embed.cc/embedmovie/{tmdb_id}"
                # للمسلسلات: يجب أن يكون المسار /embedtv/ID&s=1&e=1
                else:
                    watch_url = f"https://www.2embed.cc/embedtv/{tmdb_id}&s=1&e=1"

                new_results.append({
                    "title": title,
                    "poster": f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}",
                    "category": "أفلام" if m_type == 'movie' else "مسلسلات",
                    "episodes": [{"name": "تشغيل السيرفر الرئيسي", "url": watch_url}]
                })
            time.sleep(0.1)
        except: continue
    return new_results

def update_github_smartly():
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

    new_items = get_extensive_content()
    
    # منع التكرار بناءً على الرابط
    existing_urls = {item['episodes'][0]['url'] for item in old_data if item.get('episodes')}
    
    added_count = 0
    for item in new_items:
        if item['episodes'][0]['url'] not in existing_urls:
            old_data.append(item)
            added_count += 1
    
    # الاحتفاظ بآخر 5000 عنصر لضمان خفة الموقع
    final_data = old_data[-5000:] 

    content_encoded = base64.b64encode(json.dumps(final_data, indent=2, ensure_ascii=False).encode('utf-8')).decode('utf-8')
    payload = {
        "message": f"إضافة {added_count} عنصر جديد بروابط مصححة",
        "content": content_encoded,
        "sha": sha
    }
    
    put_res = requests.put(api_url, headers=headers, json=payload)
    if put_res.status_code in [200, 201]:
        print(f"🚀 تم بنجاح! المجموع الكلي الآن: {len(final_data)}")
    else:
        print(f"❌ فشل الرفع: {put_res.text}")

if __name__ == "__main__":
    update_github_smartly()
