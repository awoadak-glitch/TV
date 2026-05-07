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

def get_content_with_subs():
    print("🎬 جاري سحب الأفلام وتفعيل خيارات الترجمة...")
    new_results = []
    
    # صفحات عشوائية للتنوع
    random_pages = random.sample(range(1, 100), 10) 
    
    for page in random_pages:
        try:
            url = f"https://api.themoviedb.org/3/trending/all/week?api_key={TMDB_API_KEY}&language=ar&page={page}"
            res = requests.get(url, timeout=15).json()
            
            for item in res.get('results', []):
                tmdb_id = item.get('id')
                m_type = item.get('media_type', 'movie')
                title = item.get('title') if m_type == 'movie' else item.get('name')
                
                if not title or not tmdb_id: continue

                # --- حلول الترجمة ---
                # 1. سيرفر 2Embed مع أمر اللغة العربية
                s1_url = f"https://www.2embed.cc/embed{'movie' if m_type == 'movie' else 'tv'}/{tmdb_id}{'' if m_type == 'movie' else '&s=1&e=1'}&lang=ar"
                
                # 2. سيرفر Vidsrc.pro (الأفضل حالياً في الترجمة التلقائية)
                s2_url = f"https://vidsrc.pro/embed/{m_type}/{tmdb_id}{'' if m_type == 'movie' else '/1/1'}"

                new_results.append({
                    "title": title,
                    "poster": f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}",
                    "category": "أفلام" if m_type == 'movie' else "مسلسلات",
                    "episodes": [
                        {"name": "سيرفر 1 (ترجمة يدوية - اضغط CC)", "url": s1_url},
                        {"name": "سيرفر 2 (ترجمة تلقائية - مدمجة)", "url": s2_url}
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

    new_items = get_content_with_subs()
    
    # منع التكرار
    existing_titles = {item['title'] for item in old_data}
    for item in new_items:
        if item['title'] not in existing_titles:
            old_data.append(item)
    
    # الاحتفاظ بآخر 10,000
    final_data = old_data[-10000:] 

    content_encoded = base64.b64encode(json.dumps(final_data, indent=2, ensure_ascii=False).encode('utf-8')).decode('utf-8')
    payload = {
        "message": "تحديث السيرفرات لدعم الترجمة العربية",
        "content": content_encoded,
        "sha": sha
    }
    
    requests.put(api_url, headers=headers, json=payload)
    print(f"🚀 تم التحديث بنجاح! المجموع: {len(final_data)}")

if __name__ == "__main__":
    update_github()
