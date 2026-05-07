import os
import requests
import json
import base64
import time

# الإعدادات - تأكد من وجود السر MY_GITHUB_TOKEN في إعدادات ريبو GitHub
GITHUB_TOKEN = os.getenv("MY_GITHUB_TOKEN")
TMDB_API_KEY = "62571b988e8d17fac56d5240f5610ef0"
REPO_NAME = "awoadak-glitch/TV"
FILE_PATH = "data.json"

def get_100_working_items():
    print("🎬 جاري سحب 100 عنصر ودمج روابط 2Embed الشغالة...")
    results = []
    
    # سحب 5 صفحات لضمان الوصول لـ 100 عنصر
    for page in range(1, 6):
        try:
            url = f"https://api.themoviedb.org/3/trending/all/week?api_key={TMDB_API_KEY}&language=ar&page={page}"
            response = requests.get(url, timeout=15).json()
            
            for item in response.get('results', []):
                tmdb_id = item.get('id')
                media_type = item.get('media_type', 'movie')
                title = item.get('title') if media_type == 'movie' else item.get('name')
                poster_path = item.get('poster_path')

                if not title or not tmdb_id:
                    continue

                # --- دمج الطريقة الصحيحة لسيرفر 2Embed ---
                if media_type == 'movie':
                    # الرابط المعتمد للأفلام
                    watch_url = f"https://www.2embed.cc/embedmovie/{tmdb_id}"
                else:
                    # الرابط المعتمد للمسلسلات (الموسم 1 الحلقة 1)
                    watch_url = f"https://www.2embed.cc/embedtv/{tmdb_id}&s=1&e=1"

                results.append({
                    "title": title,
                    "poster": f"https://image.tmdb.org/t/p/w500{poster_path}",
                    "category": "أفلام" if media_type == 'movie' else "مسلسلات",
                    "episodes": [
                        {"name": "تشغيل السيرفر الرئيسي ✅", "url": watch_url}
                    ]
                })
            time.sleep(0.3)
        except Exception as e:
            print(f"⚠️ خطأ: {e}")
            
    return results

def upload_to_github(new_data):
    api_url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # الحصول على SHA للملف الحالي لتحديثه
    get_res = requests.get(api_url, headers=headers)
    if get_res.status_code != 200:
        print("❌ تعذر العثور على الملف")
        return
        
    file_sha = get_res.json()['sha']
    
    # تحويل البيانات إلى Base64
    json_content = json.dumps(new_data, indent=2, ensure_ascii=False)
    encoded_content = base64.b64encode(json_content.encode('utf-8')).decode('utf-8')
    
    payload = {
        "message": "دمج سيرفر 2Embed لـ 100 عنصر",
        "content": encoded_content,
        "sha": file_sha
    }
    
    put_res = requests.put(api_url, headers=headers, json=payload)
    if put_res.status_code in [200, 201]:
        print(f"🚀 تم بنجاح! موقعك الآن يحتوي على {len(new_data)} فيلم ومسلسل بروابط 2Embed.")
    else:
        print(f"❌ فشل الرفع: {put_res.text}")

if __name__ == "__main__":
    final_results = get_100_working_items()
    if final_results:
        upload_to_github(final_results)
