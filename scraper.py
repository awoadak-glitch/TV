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

def get_real_working_content():
    print("🚀 جاري سحب البيانات بنظام الـ Multi-Server API...")
    results = []
    
    # سحب عشوائي لضمان التنوع
    pages = random.sample(range(1, 100), 10) 
    
    for page in pages:
        try:
            # جلب الأفلام من TMDB للحصول على البيانات الأساسية
            url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&language=ar&sort_by=popularity.desc&page={page}"
            res = requests.get(url, timeout=15).json()
            
            for item in res.get('results', []):
                tmdb_id = item.get('id')
                title = item.get('title')
                if not title or not tmdb_id: continue

                # هذه الروابط "تولد" المشغل الذي يحتوي على السيرفرات (Dood, OK, Mp4Upload)
                # الموقع vidsrc.cc و vidsrc.to هما المصدر الحقيقي لهذه السيرفرات
                server_vidsrc = f"https://vidsrc.cc/v2/embed/movie/{tmdb_id}"
                server_super = f"https://multiembed.mov/directstream.php?video_id={tmdb_id}&tmdb=1"
                
                results.append({
                    "title": title,
                    "poster": f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}",
                    "category": "أفلام",
                    "episodes": [
                        {"name": "سيرفر DoodStream/OK (عبر Vidsrc)", "url": server_vidsrc},
                        {"name": "سيرفر مباشر Mp4Upload", "url": server_super}
                    ]
                })
        except Exception as e:
            print(f"⚠️ خطأ في الصفحة {page}: {e}")
            continue
    return results

def update_github():
    api_url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    # 1. جلب الملف القديم
    res = requests.get(api_url, headers=headers)
    old_data = []
    sha = None
    if res.status_code == 200:
        f_info = res.json()
        sha = f_info['sha']
        old_data = json.loads(base64.b64decode(f_info['content']).decode('utf-8'))

    # 2. جلب البيانات الجديدة
    new_data = get_real_working_content()
    
    # 3. دمج ومنع التكرار
    existing = {i['title'] for i in old_data}
    for item in new_data:
        if item['title'] not in existing:
            old_data.append(item)
    
    # 4. تحديث GitHub
    final_content = base64.b64encode(json.dumps(old_data[-10000:], indent=2, ensure_ascii=False).encode('utf-8')).decode('utf-8')
    payload = {"message": "تحديث السيرفرات الشغالة", "content": final_content, "sha": sha}
    
    r = requests.put(api_url, headers=headers, json=payload)
    if r.status_code in [200, 201]:
        print(f"✅ تم بنجاح! الإجمالي: {len(old_data)}")
    else:
        print(f"❌ فشل: {r.text}")

if __name__ == "__main__":
    update_github()
