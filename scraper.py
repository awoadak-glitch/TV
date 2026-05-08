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
    print("📡 جاري جلب الروابط الحقيقية من سيرفرات فك التشفير...")
    new_results = []
    
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

                # --- الحل الذكي: استخدام API يجمع السيرفرات (Dood, OK, etc) ---
                # هذه الروابط هي الـ APIs التي تستخدمها مواقع الأنمي الكبرى
                
                # السيرفر 1: vidsrc.xyz (يدعم DoodStream و Mp4Upload تلقائياً في القائمة)
                s1 = f"https://vidsrc.xyz/embed/{m_type}/{tmdb_id}"
                
                # السيرفر 2: vidsrc.cc (يوفر سيرفرات OK.ru و UpToStream)
                s2 = f"https://vidsrc.cc/v2/embed/{m_type}/{tmdb_id}"
                
                # السيرفر 3: 2embed (المصدر البديل الأكثر استقراراً)
                s3 = f"https://www.2embed.cc/embed/{tmdb_id}"

                new_results.append({
                    "title": title,
                    "poster": f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}",
                    "category": "أفلام" if m_type == 'movie' else "مسلسلات",
                    "episodes": [
                        {"name": "سيرفر (Dood/Mp4) 🎥", "url": s1},
                        {"name": "سيرفر (OK.ru/Mix) 🚀", "url": s2},
                        {"name": "سيرفر احتياطي 🛠️", "url": s3}
                    ]
                })
            time.sleep(0.1)
        except: continue
    return new_results

# ... (بقية دوال التحديث لـ GitHub كما هي في الكود السابق)
