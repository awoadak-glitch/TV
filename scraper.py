import os
import requests
import json
import base64
import time

# الإعدادات
GITHUB_TOKEN = os.getenv("MY_GITHUB_TOKEN")
TMDB_API_KEY = "62571b988e8d17fac56d5240f5610ef0"
REPO_NAME = "awoadak-glitch/TV"
FILE_PATH = "data.json"

def get_100_best_items():
    print("🎬 جاري تحضير 100 عنصر مع نظام السيرفرات الاحتياطية...")
    all_data = []
    
    for page in range(1, 6): # سحب 100 عنصر
        try:
            url = f"https://api.themoviedb.org/3/trending/all/week?api_key={TMDB_API_KEY}&language=ar&page={page}"
            res = requests.get(url, timeout=15).json()
            
            for item in res.get('results', []):
                tmdb_id = item.get('id')
                m_type = item.get('media_type', 'movie')
                title = item.get('title') if m_type == 'movie' else item.get('name')
                
                if not title: continue

                # تركيب الروابط لثلاثة سيرفرات مختلفة لضمان التشغيل
                # سيرفر 1 (vidsrc.me) - الأكثر استقراراً
                s1 = f"https://vidsrc.me/embed/{'movie' if m_type == 'movie' else 'tv'}?tmdb={tmdb_id}"
                # سيرفر 2 (vidsrc.xyz) - بديل قوي
                s2 = f"https://vidsrc.xyz/embed/{'movie' if m_type == 'movie' else 'tv'}?tmdb={tmdb_id}"
                # سيرفر 3 (superembed) - احتياطي
                s3 = f"https://multiembed.mov/?video_id={tmdb_id}&tmdb=1"

                all_data.append({
                    "title": title,
                    "poster": f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}",
                    "category": "أفلام" if m_type == 'movie' else "مسلسلات",
                    "episodes": [
                        {"name": "سيرفر 1 (رئيسي)", "url": s1},
                        {"name": "سيرفر 2 (سريع)", "url": s2},
                        {"name": "سيرفر 3 (احتياطي)", "url": s3}
                    ]
                })
            time.sleep(0.2)
        except: continue
    return all_data

def upload_to_github(data):
    api_url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    res = requests.get(api_url, headers=headers)
    if res.status_code == 200:
        sha = res.json()['sha']
        content = base64.b64encode(json.dumps(data, indent=2, ensure_ascii=False).encode('utf-8')).decode('utf-8')
        payload = {"message": "تحديث 100 عنصر بنظام السيرفرات المتعددة", "content": content, "sha": sha}
        requests.put(api_url, headers=headers, json=payload)
        print(f"✅ تم الرفع! موقعك الآن يحتوي على {len(data)} عنصر مع خيارات تشغيل متعددة.")

if __name__ == "__main__":
    mega_data = get_100_best_items()
    if mega_data:
        upload_to_github(mega_data)
