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

def get_translated_api_content():
    print("🚀 جاري جلب المحتوى بنظام الـ API المترجم...")
    new_results = []
    
    # اختيار 20 صفحة عشوائية لزيادة المحتوى بسرعة
    random_pages = random.sample(range(1, 500), 20) 
    
    for page in random_pages:
        try:
            url = f"https://api.themoviedb.org/3/trending/all/week?api_key={TMDB_API_KEY}&language=ar&page={page}"
            res = requests.get(url, timeout=15).json()
            
            for item in res.get('results', []):
                tmdb_id = item.get('id')
                m_type = item.get('media_type', 'movie')
                title = item.get('title') if m_type == 'movie' else item.get('name')
                
                if not title or not tmdb_id: continue

                # --- روابط API تدعم الترجمة العربية التلقائية ---
                
                # السيرفر 1: vidsrc.cc (يدعم الترجمة عبر بارامتر sub.ar)
                s1 = f"https://vidsrc.cc/v2/embed/{m_type}/{tmdb_id}?autoar=1"
                
                # السيرفر 2: embed.su (يوفر واجهة API حديثة مع ترجمة مدمجة)
                s2 = f"https://embed.su/embed/{m_type}/{tmdb_id}"

                new_results.append({
                    "title": title,
                    "poster": f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}",
                    "category": "أفلام" if m_type == 'movie' else "مسلسلات",
                    "episodes": [
                        {"name": "سيرفر الترجمة الآلية 🌐", "url": s1},
                        {"name": "سيرفر البث المباشر ⚡", "url": s2}
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

    new_items = get_translated_api_content()
    
    # منع التكرار بناءً على الـ ID لضمان دقة 100%
    existing_ids = {item['episodes'][0]['url'].split('/')[-1].split('?')[0] for item in old_data if item.get('episodes')}
    
    added_count = 0
    for item in new_items:
        current_id = str(item['episodes'][0]['url'].split('/')[-1].split('?')[0])
        if current_id not in existing_ids:
            old_data.append(item)
            added_count += 1
    
    # رفع السقف لـ 10,000 عنصر
    final_data = old_data[-10000:] 

    content_encoded = base64.b64encode(json.dumps(final_data, indent=2, ensure_ascii=False).encode('utf-8')).decode('utf-8')
    payload = {
        "message": f"إضافة {added_count} عنصر بنظام الترجمة v5",
        "content": content_encoded,
        "sha": sha
    }
    
    requests.put(api_url, headers=headers, json=payload)
    print(f"✅ المجموع الكلي: {len(final_data)} فيلم ومسلسل مترجم.")

if __name__ == "__main__":
    update_github()
