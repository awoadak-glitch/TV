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

def get_stable_content():
    print("🚀 جاري جلب المحتوى باستخدام روابط bypass للحظر...")
    new_results = []
    
    # صفحات عشوائية لضمان الوصول لـ 10,000 عنصر تدريجياً
    random_pages = random.sample(range(1, 500), 15) 
    
    for page in random_pages:
        try:
            url = f"https://api.themoviedb.org/3/trending/all/week?api_key={TMDB_API_KEY}&language=ar&page={page}"
            res = requests.get(url, timeout=15).json()
            
            for item in res.get('results', []):
                tmdb_id = item.get('id')
                m_type = item.get('media_type', 'movie')
                title = item.get('title') if m_type == 'movie' else item.get('name')
                
                if not title or not tmdb_id: continue

                # --- السيرفرات التي صمدت معك وتدعم الترجمة العربية ---
                
                # 1. السيرفر الأساسي (2Embed) مع إضافة كود لغة المشغل
                # أضفنا &set_lang=ar لمحاولة إجبار الواجهة على التحول للعربية
                s1 = f"https://www.2embed.cc/embed{'movie' if m_type == 'movie' else 'tv'}/{tmdb_id}{'' if m_type == 'movie' else '&s=1&e=1'}&set_lang=ar"
                
                # 2. السيرفر البديل (NonoStream) - سيرفر قديم لكنه يفتح في أغلب المناطق
                s2 = f"https://www.NonoStream.com/embed/{m_type}/{tmdb_id}"

                new_results.append({
                    "title": title,
                    "poster": f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}",
                    "category": "أفلام" if m_type == 'movie' else "مسلسلات",
                    "episodes": [
                        {"name": "سيرفر 1 (شغال ✅ - اضغط CC للترجمة)", "url": s1},
                        {"name": "سيرفر 2 (احتياطي 🔄)", "url": s2}
                    ]
                })
            time.sleep(0.1)
        except: continue
    return new_results

def update_github():
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

    new_items = get_stable_content()
    
    # منع التكرار
    existing_titles = {item['title'] for item in old_data}
    for item in new_items:
        if item['title'] not in existing_titles:
            old_data.append(item)
    
    # رفع السعة لـ 10,000 تدريجياً
    final_data = old_data[-10000:] 

    content_encoded = base64.b64encode(json.dumps(final_data, indent=2, ensure_ascii=False).encode('utf-8')).decode('utf-8')
    payload = {
        "message": "تحديث روابط Bypass ودعم 10,000 عنصر",
        "content": content_encoded,
        "sha": sha
    }
    
    requests.put(api_url, headers=headers, json=payload)
    print(f"✅ المجموع الحالي: {len(final_data)} عنصر. جرب الآن!")

if __name__ == "__main__":
    update_github()
