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
    print("🎬 جاري سحب محتوى جديد ومكثف...")
    new_results = []
    
    # سنختار 25 صفحة عشوائية من أول 500 صفحة في TMDB لجلب أفلام متنوعة وغير مكررة
    random_pages = random.sample(range(1, 500), 25) 
    
    for page in random_pages:
        try:
            # نستخدم اكتشاف الأفلام (discover) بدلاً من الرائج فقط لجلب كميات ضخمة
            url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&language=ar&sort_by=popularity.desc&page={page}"
            res = requests.get(url, timeout=15).json()
            
            for item in res.get('results', []):
                tmdb_id = item.get('id')
                title = item.get('title')
                if not title or not tmdb_id: continue

                new_results.append({
                    "title": title,
                    "poster": f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}",
                    "category": "أفلام",
                    "episodes": [{"name": "مشاهدة الآن", "url": f"https://www.2embed.cc/embedmovie/{tmdb_id}"}]
                })
            time.sleep(0.1) # سرعة معقولة لتجنب الحظر
        except: continue
    return new_results

def update_github_smartly():
    api_url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    # 1. جلب البيانات القديمة
    res = requests.get(api_url, headers=headers)
    old_data = []
    sha = None
    if res.status_code == 200:
        file_info = res.json()
        sha = file_info['sha']
        content = base64.b64decode(file_info['content']).decode('utf-8')
        old_data = json.loads(content)

    # 2. جلب البيانات الجديدة
    new_items = get_extensive_content()
    
    # 3. الدمج الذكي (منع التكرار بناءً على الـ ID)
    # نستخرج الروابط الموجودة فعلياً لمنع التكرار
    existing_urls = {item['episodes'][0]['url'] for item in old_data if item.get('episodes')}
    
    added_count = 0
    for item in new_items:
        current_url = item['episodes'][0]['url']
        if current_url not in existing_urls:
            old_data.append(item)
            existing_urls.add(current_url)
            added_count += 1
    
    # 4. الرفع (سنبقي الملف بحد أقصى 5000 عنصر حالياً لضمان سرعة الموقع)
    final_data = old_data[-5000:] 

    content_encoded = base64.b64encode(json.dumps(final_data, indent=2, ensure_ascii=False).encode('utf-8')).decode('utf-8')
    payload = {
        "message": f"إضافة {added_count} عنصر جديد (المجموع: {len(final_data)})",
        "content": content_encoded,
        "sha": sha
    }
    
    put_res = requests.put(api_url, headers=headers, json=payload)
    if put_res.status_code in [200, 201]:
        print(f"🚀 نجاح! أضفنا {added_count} فيلم جديد. المجموع الكلي الآن: {len(final_data)}")
    else:
        print(f"❌ فشل الرفع: {put_res.text}")

if __name__ == "__main__":
    update_github_smartly()
