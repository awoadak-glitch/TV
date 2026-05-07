import requests
import json
import base64
import time

# --- إعداداتك الخاصة ---
GITHUB_TOKEN = "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"
TMDB_API_KEY = "62571b988e8d17fac56d5240f5610ef0"
REPO_NAME = "awoadak-glitch/TV"
FILE_PATH = "data.json"

# سيرفرات Consumet المتاحة (لضمان عمل الأنمي دائماً)
CONSUMET_SERVERS = [
    "https://consumet-api-production-e650.up.railway.app",
    "https://api-consumet-org-three.vercel.app",
    "https://api.consumet.org"
]

def get_tmdb_bulk(total_needed=100):
    """سحب كمية كبيرة من الأفلام والمسلسلات الرائجة"""
    results = []
    page = 1
    print(f"🎬 جاري جمع {total_needed} فيلم ومسلسل من TMDB...")
    
    while len(results) < total_needed and page <= 10:
        url = f"https://api.themoviedb.org/3/trending/all/week?api_key={TMDB_API_KEY}&language=ar&page={page}"
        try:
            res = requests.get(url, timeout=15)
            if res.status_code == 200:
                data = res.json()
                for item in data.get('results', []):
                    is_movie = item.get('media_type') == 'movie'
                    title = item.get('title') if is_movie else item.get('name')
                    tmdb_id = item.get('id')
                    
                    # نظام المشغل المباشر
                    v_url = f"https://vidsrc.to/embed/movie/{tmdb_id}" if is_movie else f"https://vidsrc.to/embed/tv/{tmdb_id}/1/1"
                    
                    results.append({
                        "title": title,
                        "poster": f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}",
                        "category": "أفلام" if is_movie else "مسلسلات",
                        "episodes": [{"name": "مشاهدة الآن", "url": v_url}]
                    })
                    if len(results) >= total_needed: break
            page += 1
            time.sleep(0.3)
        except: break
    return results

def get_anime_bulk():
    """سحب أحدث حلقات الأنمي مع تجربة عدة سيرفرات"""
    results = []
    print("🐉 جاري البحث عن حلقات الأنمي الجديدة...")
    
    for server in CONSUMET_SERVERS:
        try:
            # نسحب من Gogoanime كخيار أول
            res = requests.get(f"{server}/anime/gogoanime/recent-episodes", timeout=10)
            if res.status_code == 200:
                for item in res.json().get('results', []):
                    results.append({
                        "title": item.get('title'),
                        "poster": item.get('image'),
                        "category": "أنمي",
                        "episodes": [{"name": f"الحلقة {item.get('episodeNumber')}", "url": f"{server}/anime/gogoanime/watch/{item.get('episodeId')}"}]
                    })
                if results: break # إذا نجح سيرفر نتوقف
        except: continue
    return results

def update_github(new_data):
    api_url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    # جلب الملف الحالي لدمجه
    res = requests.get(api_url, headers=headers)
    if res.status_code != 200: return
    
    file_info = res.json()
    db = json.loads(base64.b64decode(file_info['content']).decode('utf-8'))
    
    # منع التكرار بناءً على العنوان
    existing_titles = {item['title'] for item in db}
    added_count = 0
    
    for item in new_data:
        if item['title'] not in existing_titles:
            db.append(item)
            added_count += 1
            
    if added_count > 0:
        updated_db = json.dumps(db, indent=2, ensure_ascii=False)
        payload = {
            "message": f"تحديث تلقائي ضخم: إضافة {added_count} عنصر",
            "content": base64.b64encode(updated_db.encode('utf-8')).decode('utf-8'),
            "sha": file_info['sha']
        }
        requests.put(api_url, headers=headers, json=payload)
        print(f"✅ مبروك! تم إضافة {added_count} عنصر جديد بنجاح.")
    else:
        print("😴 لا يوجد محتوى جديد حالياً.")

if __name__ == "__main__":
    # تشغيل السحب الضخم
    all_content = get_tmdb_bulk(100) + get_anime_bulk()
    if all_content:
        update_github(all_content)
    else:
        print("🛑 فشل في جلب البيانات من كافة المصادر.")
