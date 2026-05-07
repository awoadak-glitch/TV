import os
import requests
import json
import base64
import random

# الإعدادات الأساسية
GITHUB_TOKEN = os.getenv("MY_GITHUB_TOKEN")
TMDB_API_KEY = "62571b988e8d17fac56d5240f5610ef0"
REPO_NAME = "awoadak-glitch/TV"
FILE_PATH = "data.json"

def get_random_movie():
    print("🔍 جاري اختيار فيلم عشوائي برابط صحيح...")
    # اختيار صفحة عشوائية من أول 10 صفحات لجلب تنوع أكبر
    random_page = random.randint(1, 10)
    url = f"https://api.themoviedb.org/3/trending/all/week?api_key={TMDB_API_KEY}&language=ar&page={random_page}"
    
    try:
        response = requests.get(url).json()
        results = response.get('results', [])
        
        if results:
            # اختيار عنصر واحد عشوائي من النتائج
            item = random.choice(results)
            tmdb_id = item.get('id')
            media_type = item.get('media_type', 'movie')
            title = item.get('title') if media_type == 'movie' else item.get('name')
            
            # تركيب رابط المشاهدة الصحيح بناءً على معرف الفيلم الحقيقي
            if media_type == 'movie':
                watch_url = f"https://vidsrc.me/embed/movie?tmdb={tmdb_id}"
            else:
                watch_url = f"https://vidsrc.me/embed/tv?tmdb={tmdb_id}&season=1&episode=1"
            
            movie_data = [{
                "title": title,
                "poster": f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}",
                "category": "أفلام" if media_type == 'movie' else "مسلسلات",
                "episodes": [{"name": "مشاهدة الآن", "url": watch_url}]
            }]
            print(f"✅ تم اختيار فيلم: {title}")
            return movie_data
        return None
    except Exception as e:
        print(f"⚠️ خطأ: {e}")
        return None

def upload_to_github(data):
    api_url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    # جلب SHA للملف لتحديثه
    res = requests.get(api_url, headers=headers)
    if res.status_code == 200:
        sha = res.json()['sha']
        content = base64.b64encode(json.dumps(data, indent=2, ensure_ascii=False).encode('utf-8')).decode('utf-8')
        
        payload = {
            "message": f"تحديث فيلم عشوائي: {data[0]['title']}",
            "content": content,
            "sha": sha
        }
        
        requests.put(api_url, headers=headers, json=payload)
        print(f"🚀 مبروك! تم رفع الفيلم بنجاح.")

if __name__ == "__main__":
    random_item = get_random_movie()
    if random_item:
        upload_to_github(random_item)
