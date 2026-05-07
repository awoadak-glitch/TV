import requests
import json
import base64

# --- البيانات الأساسية ---
# تأكد أن التوكن الذي وضعته هو الأخير الذي يبدأ بـ Github_pat_...
GITHUB_TOKEN = "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"
TMDB_API_KEY = "62571b988e8d17fac56d5240f5610ef0"
REPO_NAME = "awoadak-glitch/TV"
FILE_PATH = "data.json"

def scrape_single_movie():
    print("🎬 جاري محاولة سحب فيلم واحد فقط من TMDB للاختبار...")
    
    # رابط جلب الأفلام الأكثر شعبية
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=ar&page=1"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            movie = response.json()['results'][0] # نأخذ أول فيلم فقط
            
            single_data = {
                "title": movie['title'],
                "poster": f"https://image.tmdb.org/t/p/w500{movie['poster_path']}",
                "category": "أفلام",
                "episodes": [{
                    "name": "مشاهدة الفيلم",
                    "url": f"https://vidsrc.to/embed/movie/{movie['id']}"
                }]
            }
            print(f"✅ تم سحب الفيلم بنجاح: {movie['title']}")
            upload_to_github(single_data)
        else:
            print(f"❌ فشل سحب الفيلم من TMDB. الكود: {response.status_code}")
    except Exception as e:
        print(f"❌ حدث خطأ غير متوقع: {e}")

def upload_to_github(new_item):
    api_url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # 1. جلب محتوى الملف الحالي
    res = requests.get(api_url, headers=headers)
    if res.status_code == 200:
        file_info = res.json()
        current_content = json.loads(base64.b64decode(file_info['content']).decode('utf-8'))
        
        # 2. إضافة الفيلم الجديد للقائمة
        current_content.append(new_item)
        
        # 3. تشفير البيانات المحدثة ورفعها
        updated_json = json.dumps(current_content, indent=2, ensure_ascii=False)
        payload = {
            "message": f"إضافة فيلم تجريبي: {new_item['title']}",
            "content": base64.b64encode(updated_json.encode('utf-8')).decode('utf-8'),
            "sha": file_info['sha']
        }
        
        final_res = requests.put(api_url, headers=headers, json=payload)
        if final_res.status_code in [200, 201]:
            print(f"🚀 نجاح! تم رفع الفيلم '{new_item['title']}' إلى موقعك.")
        else:
            print(f"❌ فشل الرفع لـ GitHub. الكود: {final_res.status_code} - {final_res.text}")
    else:
        print(f"❌ لم أتمكن من الوصول لملف data.json. تأكد من التوكن وصلاحياته. الكود: {res.status_code}")

if __name__ == "__main__":
    scrape_single_movie()
