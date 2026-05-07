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

def get_new_content():
    print("🎬 جاري سحب 100 عنصر جديد...")
    new_results = []
    for page in range(1, 6):
        try:
            url = f"https://api.themoviedb.org/3/trending/all/week?api_key={TMDB_API_KEY}&language=ar&page={page}"
            res = requests.get(url, timeout=15).json()
            for item in res.get('results', []):
                tmdb_id = item.get('id')
                m_type = item.get('media_type', 'movie')
                title = item.get('title') if m_type == 'movie' else item.get('name')
                if not title or not tmdb_id: continue

                ep_list = []
                if m_type == 'movie':
                    # رابط الفيلم مع محاولة تفعيل لغة الواجهة العربية
                    watch_url = f"https://www.2embed.cc/embedmovie/{tmdb_id}"
                    ep_list.append({"name": "مشاهدة الفيلم", "url": watch_url})
                else:
                    # سحب 15 حلقة للمسلسلات
                    for i in range(1, 16):
                        watch_url = f"https://www.2embed.cc/embedtv/{tmdb_id}&s=1&e={i}"
                        ep_list.append({"name": f"الحلقة {i}", "url": watch_url})

                new_results.append({
                    "title": title,
                    "poster": f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}",
                    "category": "أفلام" if m_type == 'movie' else "مسلسلات",
                    "episodes": ep_list
                })
            time.sleep(0.2)
        except: continue
    return new_results

def update_github():
    api_url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    # 1. جلب البيانات القديمة الموجودة في الملف حالياً
    res = requests.get(api_url, headers=headers)
    old_data = []
    sha = None
    
    if res.status_code == 200:
        file_info = res.json()
        sha = file_info['sha']
        content = base64.b64decode(file_info['content']).decode('utf-8')
        old_data = json.loads(content)
    
    # 2. جلب البيانات الجديدة
    new_items = get_new_content()
    
    # 3. الدمج بدون تكرار (بناءً على العنوان)
    existing_titles = {item['title'] for item in old_data}
    for item in new_items:
        if item['title'] not in existing_titles:
            old_data.append(item)
    
    # اختياري: الاحتفاظ بآخر 500 فيلم فقط لكي لا يصبح الملف ثقيلاً جداً
    final_data = old_data[-500:]

    # 4. الرفع إلى GitHub
    content_encoded = base64.b64encode(json.dumps(final_data, indent=2, ensure_ascii=False).encode('utf-8')).decode('utf-8')
    payload = {
        "message": f"إضافة أفلام جديدة (المجموع الحالي: {len(final_data)})",
        "content": content_encoded,
        "sha": sha
    }
    
    put_res = requests.put(api_url, headers=headers, json=payload)
    if put_res.status_code in [200, 201]:
        print(f"🚀 تم التحديث! الملف الآن يحتوي على {len(final_data)} فيلم ومسلسل.")
    else:
        print(f"❌ فشل الرفع: {put_res.text}")

if __name__ == "__main__":
    update_github()
