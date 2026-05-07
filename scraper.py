import os
import requests
import json
import base64
import time

# الإعدادات - تأكد من وجود السر MY_GITHUB_TOKEN
GITHUB_TOKEN = os.getenv("MY_GITHUB_TOKEN")
TMDB_API_KEY = "62571b988e8d17fac56d5240f5610ef0"
REPO_NAME = "awoadak-glitch/TV"
FILE_PATH = "data.json"

def get_verified_content():
    print("🎬 جاري جلب 100 عنصر مع أقوى سيرفرات المشاهدة العالمية...")
    results = []
    
    for page in range(1, 6):
        try:
            url = f"https://api.themoviedb.org/3/trending/all/week?api_key={TMDB_API_KEY}&language=ar&page={page}"
            res = requests.get(url, timeout=15).json()
            
            for item in res.get('results', []):
                tmdb_id = item.get('id')
                m_type = item.get('media_type', 'movie')
                title = item.get('title') if m_type == 'movie' else item.get('name')
                
                if not title: continue

                # --- نظام السيرفرات المتعددة لتفادي "رفض الاتصال" ---
                # سيرفر 1: Vidsrc.xyz (الجيل الجديد)
                s1 = f"https://vidsrc.xyz/embed/{'movie' if m_type == 'movie' else 'tv'}?tmdb={tmdb_id}"
                
                # سيرفر 2: SuperEmbed (مستقر جداً ونادراً ما يُحظر)
                s2 = f"https://multiembed.mov/?video_id={tmdb_id}&tmdb=1"
                
                # سيرفر 3: 2Embed (الاحتياطي العالمي)
                s3 = f"https://www.2embed.cc/embed{'movie' if m_type == 'movie' else 'tv'}?tmdb={tmdb_id}"

                results.append({
                    "title": title,
                    "poster": f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}",
                    "category": "أفلام" if m_type == 'movie' else "مسلسلات",
                    "episodes": [
                        {"name": "السيرفر الأساسي (vidsrc)", "url": s1},
                        {"name": "السيرفر السريع (Super)", "url": s2},
                        {"name": "سيرفر الطوارئ (2Embed)", "url": s3}
                    ]
                })
            time.sleep(0.3)
        except: continue
            
    return results

def upload_to_github(data):
    api_url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    res = requests.get(api_url, headers=headers)
    if res.status_code == 200:
        sha = res.json()['sha']
        content = base64.b64encode(json.dumps(data, indent=2, ensure_ascii=False).encode('utf-8')).decode('utf-8')
        payload = {"message": "تحديث 100 عنصر بسيرفرات عالمية", "content": content, "sha": sha}
        requests.put(api_url, headers=headers, json=payload)
        print(f"✅ مبروك! موقعك يحتوي الآن على {len(data)} عنصر جاهزة للمشاهدة.")

if __name__ == "__main__":
    final_data = get_verified_content()
    if final_data:
        upload_to_github(final_data)
