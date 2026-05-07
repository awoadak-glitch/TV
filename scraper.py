import requests
import json
import base64
import time

# --- البيانات الجديدة المحدثة ---
GITHUB_TOKEN = "Github_pat_11BU54UEA08TwphdqgNyzF_dgQtU7REqDVPkzcUDhcvg4YKkRMW1IRCoUJhF6a7dIVWA2MTAAVGTWyEUZp"
TMDB_API_KEY = "62571b988e8d17fac56d5240f5610ef0"
REPO_NAME = "awoadak-glitch/TV"
FILE_PATH = "data.json"

def get_bulk_content():
    all_results = []
    
    # 1. سحب 100 فيلم ومسلسل (من أول 5 صفحات في TMDB)
    print("🎬 جاري سحب 100 عنصر من الأفلام والمسلسلات...")
    for page in range(1, 6):
        try:
            url = f"https://api.themoviedb.org/3/trending/all/week?api_key={TMDB_API_KEY}&language=ar&page={page}"
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                data = response.json()
                for item in data.get('results', []):
                    is_movie = item.get('media_type') == 'movie'
                    title = item.get('title') if is_movie else item.get('name')
                    if not title: continue
                    
                    all_results.append({
                        "title": title,
                        "poster": f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}",
                        "category": "أفلام" if is_movie else "مسلسلات",
                        "episodes": [{"name": "مشاهدة الآن", "url": f"https://vidsrc.to/embed/{'movie' if is_movie else 'tv'}/{item.get('id')}"}]
                    })
            time.sleep(0.2)
        except: continue

    # 2. سحب الأنمي من السيرفر الرسمي
    print("🐉 جاري سحب أحدث حلقات الأنمي...")
    try:
        anime_url = "https://api.consumet.org/anime/gogoanime/recent-episodes"
        res = requests.get(anime_url, timeout=15).json()
        for anime in res.get('results', []):
            all_results.append({
                "title": anime['title'],
                "poster": anime['image'],
                "category": "أنمي",
                "episodes": [{"name": f"الحلقة {anime['episodeNumber']}", "url": f"https://api.consumet.org/anime/gogoanime/watch/{anime['episodeId']}"}]
            })
    except:
        print("⚠️ سيرفر الأنمي لم يستجب، سنكتفي بالأفلام حالياً.")

    return all_results

def update_github(data):
    api_url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # جلب الملف الحالي لدمجه
    res = requests.get(api_url, headers=headers)
    if res.status_code != 200:
        print(f"❌ فشل الاتصال بجيت هاب. كود الخطأ: {res.status_code}")
        return

    file_info = res.json()
    current_db = json.loads(base64.b64decode(file_info['content']).decode('utf-8'))
    
    # منع التكرار بناءً على العنوان
    existing_titles = {item['title'] for item in current_db}
    new_count = 0
    for item in data:
        if item['title'] not in existing_titles:
            current_db.append(item)
            new_count += 1

    if new_count > 0:
        updated_content = base64.b64encode(json.dumps(current_db, indent=2, ensure_ascii=False).encode('utf-8')).decode('utf-8')
        payload = {
            "message": f"تحديث ضخم: إضافة {new_count} مادة جديدة",
            "content": updated_content,
            "sha": file_info['sha']
        }
        put_res = requests.put(api_url, headers=headers, json=payload)
        if put_res.status_code in [200, 201]:
            print(f"🚀 نجاح باهر! تم إضافة {new_count} عنصر جديد لموقعك.")
        else:
            print(f"❌ فشل الرفع: {put_res.text}")
    else:
        print("😴 لا يوجد محتوى جديد لإضافته، كل شيء محدث.")

if __name__ == "__main__":
    final_data = get_bulk_content()
    if final_data:
        update_github(final_data)
    else:
        print("🛑 لم يتم العثور على أي بيانات لسحبها.")
