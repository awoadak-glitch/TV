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

def get_pro_api_content():
    print("🎬 جاري جلب محتوى من مجمعات الـ API الاحترافية...")
    new_results = []
    
    # سحب عشوائي لضمان الوصول لـ 10,000 تدريجياً
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

                # --- روابط تحاكي الـ APIs المستخدمة في التطبيقات الاحترافية ---
                
                # السيرفر 1: Vidsrc.to (المنافس الأقوى حالياً - يدعم الترجمة التلقائية)
                s1 = f"https://vidsrc.to/embed/{m_type}/{tmdb_id}"
                
                # السيرفر 2: Cineapi (نظام جديد يحاول توفير روابط سريعة ومترجمة)
                s2 = f"https://api.cineapi.xyz/embed/{m_type}/{tmdb_id}"

                new_results.append({
                    "title": title,
                    "poster": f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}",
                    "category": "أفلام" if m_type == 'movie' else "مسلسلات",
                    "episodes": [
                        {"name": "سيرفر البث الاحترافي (VIP)", "url": s1},
                        {"name": "سيرفر الترجمة الفورية (AUTO)", "url": s2}
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
        content = base64.decodebytes(file_info['content'].encode()).decode('utf-8')
        old_data = json.loads(content)

    new_items = get_pro_api_content()
    
    # منع التكرار لضمان بناء قاعدة بيانات تصل لـ 10,000 عنصر
    existing_titles = {item['title'] for item in old_data}
    for item in new_items:
        if item['title'] not in existing_titles:
            old_data.append(item)
    
    # الحفاظ على آخر 10,000 عنصر
    final_data = old_data[-10000:] 

    content_encoded = base64.b64encode(json.dumps(final_data, indent=2, ensure_ascii=False).encode('utf-8')).decode('utf-8')
    payload = {
        "message": f"تحديث API احترافي (العدد الحالي: {len(final_data)})",
        "content": content_encoded,
        "sha": sha
    }
    
    requests.put(api_url, headers=headers, json=payload)
    print(f"✅ تم الرفع! المجموع الكلي: {len(final_data)}")

if __name__ == "__main__":
    update_github()
