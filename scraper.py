import requests
import json
import base64
import time

# --- بياناتك ---
GITHUB_TOKEN = "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"
TMDB_API_KEY = "62571b988e8d17fac56d5240f5610ef0"
REPO_NAME = "awoadak-glitch/TV"
FILE_PATH = "data.json"

# قائمة سيرفرات بديلة لضمان العمل
ANIME_SERVERS = [
    "https://api.consumet.org",
    "https://consumet-api-production-e650.up.railway.app",
    "https://consumet-api-clone.vercel.app"
]

def get_tmdb_bulk(pages=5):
    results = []
    print(f"🎬 جاري محاولة سحب {pages*20} فيلم من TMDB...")
    for page in range(1, pages + 1):
        url = f"https://api.themoviedb.org/3/trending/all/week?api_key={TMDB_API_KEY}&language=ar&page={page}"
        try:
            res = requests.get(url, timeout=15)
            if res.status_code == 200:
                for item in res.json().get('results', []):
                    is_movie = item.get('media_type') == 'movie'
                    results.append({
                        "title": item.get('title') if is_movie else item.get('name'),
                        "poster": f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}",
                        "category": "أفلام" if is_movie else "مسلسلات",
                        "episodes": [{"name": "مشاهدة الآن", "url": f"https://vidsrc.to/embed/{'movie' if is_movie else 'tv'}/{item.get('id')}"}]
                    })
        except: continue
    return results

def get_anime_bulk():
    print("🐉 جاري البحث عن سيرفر أنمي مستجيب...")
    for server in ANIME_SERVERS:
        try:
            res = requests.get(f"{server}/anime/gogoanime/recent-episodes", timeout=10)
            if res.status_code == 200:
                print(f"✅ تم الاتصال بنجاح بسيرفر: {server}")
                return [{
                    "title": item['title'],
                    "poster": item['image'],
                    "category": "أنمي",
                    "episodes": [{"name": f"الحلقة {item['episodeNumber']}", "url": f"{server}/anime/gogoanime/watch/{item['episodeId']}"}]
                } for item in res.json().get('results', [])]
        except: continue
    return []

def update_github(new_data):
    api_url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    res = requests.get(api_url, headers=headers)
    if res.status_code != 200: return
    
    file_info = res.json()
    db = json.loads(base64.b64decode(file_info['content']).decode('utf-8'))
    
    existing = {item['title'] for item in db}
    added = 0
    for item in new_data:
        if item['title'] not in existing:
            db.append(item)
            added += 1
            
    if added > 0:
        new_content = base64.b64encode(json.dumps(db, indent=2, ensure_ascii=False).encode('utf-8')).decode('utf-8')
        requests.put(api_url, headers=headers, json={"message": f"سحب {added} عنصر", "content": new_content, "sha": file_info['sha']})
        print(f"🚀 مبروك! أضفنا {added} عنوان جديد.")
    else:
        print("😴 كل شيء محدث بالفعل.")

if __name__ == "__main__":
    combined_data = get_tmdb_bulk(5) + get_anime_bulk()
    if combined_data:
        update_github(combined_data)
