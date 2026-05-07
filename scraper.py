import requests
import json
import base64

# --- بياناتك ---
GITHUB_TOKEN = "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"
TMDB_API_KEY = "62571b988e8d17fac56d5240f5610ef0"
REPO_NAME = "awoadak-glitch/TV"
FILE_PATH = "data.json"

def manual_test():
    print("🛠️ بدء الاختبار اليدوي لعنصر واحد...")
    test_data = []

    # 1. تجربة سحب فيلم واحد من TMDB
    try:
        print("🎬 محاولة سحب فيلم من TMDB...")
        tmdb_url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=ar&page=1"
        res = requests.get(tmdb_url, timeout=10)
        res.raise_for_status() # سيطبع خطأ إذا فشل الاتصال
        movie = res.json()['results'][0]
        test_data.append({
            "title": movie['title'],
            "poster": f"https://image.tmdb.org/t/p/w500{movie['poster_path']}",
            "category": "أفلام",
            "episodes": [{"name": "مشاهدة", "url": f"https://vidsrc.to/embed/movie/{movie['id']}"}]
        })
        print(f"✅ نجح سحب الفيلم: {movie['title']}")
    except Exception as e:
        print(f"❌ فشل TMDB: {e}")

    # 2. تجربة سحب أنمي واحد من Consumet
    try:
        print("🐉 محاولة سحب أنمي من Consumet...")
        anime_url = "https://consumet-api-production-e650.up.railway.app/anime/gogoanime/recent-episodes"
        res = requests.get(anime_url, timeout=10)
        res.raise_for_status()
        anime = res.json()['results'][0]
        test_data.append({
            "title": anime['title'],
            "poster": anime['image'],
            "category": "أنمي",
            "episodes": [{"name": "حلقة تجريبية", "url": "https://google.com"}]
        })
        print(f"✅ نجح سحب الأنمي: {anime['title']}")
    except Exception as e:
        print(f"❌ فشل Consumet: {e}")

    # 3. محاولة الرفع لـ GitHub
    if test_data:
        print(f"📤 جاري محاولة رفع {len(test_data)} عنصر لـ GitHub...")
        update_github(test_data)
    else:
        print("⚠️ لا توجد بيانات لرفعها.")

def update_github(data):
    api_url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    res = requests.get(api_url, headers=headers)
    if res.status_code == 200:
        file_info = res.json()
        db = json.loads(base64.b64decode(file_info['content']).decode('utf-8'))
        db.extend(data)
        updated_content = base64.b64encode(json.dumps(db, indent=2, ensure_ascii=False).encode('utf-8')).decode('utf-8')
        put_res = requests.put(api_url, headers=headers, json={"message": "اختبار يدوي", "content": updated_content, "sha": file_info['sha']})
        print(f"🚀 نتيجة الرفع: {put_res.status_code}")
    else:
        print(f"❌ فشل الوصول لـ GitHub: {res.status_code}")

if __name__ == "__main__":
    manual_test()
