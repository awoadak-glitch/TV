import requests
import json
import base64
import time

# --- إعداداتك ---
GITHUB_TOKEN = "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"
TMDB_API_KEY = "62571b988e8d17fac56d5240f5610ef0"
REPO_NAME = "awoadak-glitch/TV"
FILE_PATH = "data.json"
CONSUMET_BASE = "https://consumet-api-production-e650.up.railway.app"

def get_tmdb_bulk(pages=5):
    """سحب كمية كبيرة من الأفلام والمسلسلات (20 عنصر لكل صفحة)"""
    results = []
    for page in range(1, pages + 1):
        url = f"https://api.themoviedb.org/3/trending/all/week?api_key={TMDB_API_KEY}&language=ar&page={page}"
        try:
            data = requests.get(url, timeout=10).json()
            for item in data.get('results', []):
                is_movie = item.get('media_type') == 'movie'
                tmdb_id = item.get('id')
                title = item.get('title') if is_movie else item.get('name')
                
                v_url = f"https://vidsrc.to/embed/movie/{tmdb_id}" if is_movie else f"https://vidsrc.to/embed/tv/{tmdb_id}/1/1"
                
                results.append({
                    "title": title,
                    "poster": f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}",
                    "category": "أفلام" if is_movie else "مسلسلات",
                    "episodes": [{"name": "مشاهدة الآن", "url": v_url}]
                })
            time.sleep(0.2) # تجنب الضغط على السيرفر
        except: continue
    return results

def get_anime_bulk():
    """سحب الأنمي من عدة مزودين لجمع أكبر عدد"""
    providers = ["gogoanime", "zoro", "enime"]
    results = []
    for p in providers:
        url = f"{CONSUMET_BASE}/anime/{p}/recent-episodes"
        try:
            data = requests.get(url, timeout=15).json()
            for item in data.get('results', []):
                results.append({
                    "title": item.get('title'),
                    "poster": item.get('image'),
                    "category": "أنمي",
                    "episodes": [{"name": f"الحلقة {item.get('episodeNumber')}", "url": f"{CONSUMET_BASE}/anime/{p}/watch/{item.get('episodeId')}"}]
                })
        except: continue
    return results

def update_github(new_items):
    api_url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    res = requests.get(api_url, headers=headers)
    if res.status_code != 200: return
    
    file_info = res.json()
    db = json.loads(base64.b64decode(file_info['content']).decode('utf-8'))
    
    existing_titles = {item['title'] for item in db}
    added = 0

    for item in new_items:
        if item['title'] not in existing_titles:
            db.append(item)
            added += 1
        # اختياري: يمكنك إضافة منطق لتحديث الحلقات هنا أيضاً

    if added > 0:
        new_db = json.dumps(db, indent=2, ensure_ascii=False)
        payload = {
            "message": f"سحب ضخم: إضافة {added} عنصر جديد",
            "content": base64.b64encode(new_db.encode('utf-8')).decode('utf-8'),
            "sha": file_info['sha']
        }
        requests.put(api_url, headers=headers, json=payload)
        print(f"✅ تم إضافة {added} عنوان جديد إلى مكتبتك!")
    else:
        print("😴 المكتبة محدثة بالفعل، لا يوجد جديد.")

if __name__ == "__main__":
    print("🚀 بدء عملية السحب الضخم (100+ عنصر)...")
    all_content = get_tmdb_bulk(pages=5) + get_anime_bulk()
    update_github(all_content)
