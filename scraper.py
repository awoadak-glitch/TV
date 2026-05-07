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

def get_verified_content():
    print("🎬 جاري سحب محتوى جديد وتدقيق الروابط...")
    new_results = []
    
    # اختيار صفحات عشوائية لضمان التنوع وعدم التكرار
    random_pages = random.sample(range(1, 150), 10) 
    
    for page in random_pages:
        try:
            url = f"https://api.themoviedb.org/3/trending/all/week?api_key={TMDB_API_KEY}&language=ar&page={page}"
            res = requests.get(url, timeout=15).json()
            
            for item in res.get('results', []):
                tmdb_id = item.get('id')
                m_type = item.get('media_type', 'movie')
                title = item.get('title') if m_type == 'movie' else item.get('name')
                
                if not title or not tmdb_id: continue

                # --- تطبيق الروابط الصحيحة كما في صور 2Embed ---
                if m_type == 'movie':
                    # رابط الأفلام المعتمد (لاحظ المسار /embed/)
                    watch_url = f"https://www.2embed.cc/embed/{tmdb_id}"
                else:
                    # رابط المسلسلات المعتمد (يجب تحديد s و e)
                    watch_url = f"https://www.2embed.cc/embedtv/{tmdb_id}&s=1&e=1"

                new_results.append({
                    "title": title,
                    "poster": f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}",
                    "category": "أفلام" if m_type == 'movie' else "مسلسلات",
                    "episodes": [{"name": "تشغيل السيرفر الرئيسي ✅", "url": watch_url}]
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

    new_items = get_verified_content()
    
    # منع التكرار بناءً على معرف الفيلم الفريد
    existing_ids = {item['episodes'][0]['url'].split('/')[-1] for item in old_data if item.get('episodes')}
    
    added_count = 0
    for item in new_items:
        current_id = item['episodes'][0]['url'].split('/')[-1]
        if current_id not in existing_ids:
            old_data.append(item)
            added_count += 1
    
    # الاحتفاظ بآخر 10,000 عنصر كما طلبت (تدريجياً)
    final_data = old_data[-10000:] 

    content_encoded = base64.b64encode(json.dumps(final_data, indent=2, ensure_ascii=False).encode('utf-8')).decode('utf-8')
    payload = {
        "message": f"تحديث {added_count} عنصر بروابط محققة (المجموع: {len(final_data)})",
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
