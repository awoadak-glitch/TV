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

def get_pirated_style_content():
    print("📡 جاري استخراج البيانات وربطها بسيرفرات DoodStream و OK.ru...")
    new_results = []
    
    # زيادة عدد الصفحات للسحب بكميات أكبر
    random_pages = random.sample(range(1, 500), 25) 
    
    for page in random_pages:
        try:
            url = f"https://api.themoviedb.org/3/trending/all/week?api_key={TMDB_API_KEY}&language=ar&page={page}"
            res = requests.get(url, timeout=15).json()
            
            for item in res.get('results', []):
                tmdb_id = item.get('id')
                imdb_id = item.get('imdb_id', '') # بعض النتائج تحتاج IMDB لضمان الدقة
                m_type = item.get('media_type', 'movie')
                title = item.get('title') if m_type == 'movie' else item.get('name')
                
                if not title or not tmdb_id: continue

                # --- بناء روابط السيرفرات المباشرة ---
                # ملاحظة: السيرفرات المقرصنة تستخدم محركات بحث داخلية تربط TMDB ID بملفاتهم
                
                # 1. سيرفر DoodStream (رابط استعلام ذكي)
                s1 = f"https://dood.to/e/{tmdb_id}" # ملاحظة: تحتاج أحيانا لتبديل الـ ID برابط Resolver
                
                # 2. سيرفر OK.ru (البحث عبر الوسيط)
                s2 = f"https://ok.ru/videoembed/search?q={title}"
                
                # 3. سيرفر Mp4Upload و VidSrc (المشغل الشامل الذي يجمعهم)
                # هذا الرابط هو "الجوكر" لأنه يفتح للمستخدم خيار التبديل بين Mp4Upload و DoodStream تلقائياً
                s3 = f"https://vidsrc.icu/embed/{m_type}/{tmdb_id}"

                new_results.append({
                    "title": title,
                    "poster": f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}",
                    "category": "أنمي/أفلام" if m_type == 'movie' else "مسلسلات",
                    "year": item.get('release_date', '2026')[:4] if m_type == 'movie' else item.get('first_air_date', '2026')[:4],
                    "episodes": [
                        {"name": "سيرفر DoodStream 🚀", "url": s1},
                        {"name": "سيرفر OK.ru (متعدد) 🎥", "url": s2},
                        {"name": "سيرفر Mp4Upload / مباشر ⬇️", "url": s3}
                    ]
                })
            time.sleep(0.1)
        except: continue
    return new_results

def update_github_database():
    api_url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    # جلب البيانات القديمة
    res = requests.get(api_url, headers=headers)
    old_data = []
    sha = None
    if res.status_code == 200:
        file_info = res.json()
        sha = file_info['sha']
        content = base64.b64decode(file_info['content']).decode('utf-8')
        old_data = json.loads(content)

    new_items = get_pirated_style_content()
    
    # دمج البيانات الجديدة مع القديمة ومنع التكرار
    existing_titles = {item['title'] for item in old_data}
    added_count = 0
    for item in new_items:
        if item['title'] not in existing_titles:
            old_data.append(item)
            added_count += 1
    
    # الاحتفاظ بآخر 10,000 عنصر فقط لسرعة الموقع
    final_data = old_data[-10000:] 

    content_encoded = base64.b64encode(json.dumps(final_data, indent=2, ensure_ascii=False).encode('utf-8')).decode('utf-8')
    payload = {
        "message": f"تم إضافة {added_count} عنوان جديد - الإجمالي {len(final_data)}",
        "content": content_encoded,
        "sha": sha
    }
    
    put_res = requests.put(api_url, headers=headers, json=payload)
    if put_res.status_code == 200:
        print(f"✅ تم التحديث بنجاح! قاعدة البيانات تضم الآن {len(final_data)} فيديو.")
    else:
        print(f"❌ فشل التحديث: {put_res.text}")

if __name__ == "__main__":
    update_github_database()
