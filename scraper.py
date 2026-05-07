import json
import base64
import cloudscraper
from bs4 import BeautifulSoup

# --- البيانات الخاصة بك ---
GITHUB_TOKEN = "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"
REPO_NAME = "awoadak-glitch/TV"
FILE_PATH = "data.json"

# هذه المتغيرات سيتم جلبها من الـ Workflow (المدخلات)
import os
TARGET_URL = os.getenv('GITHUB_EVENT_INPUTS_TARGET_URL') # سيتم تمريره تلقائياً من الأكشن
# ملاحظة: في حال التشغيل اليدوي من الأكشن، سنحتاج لاستخدام مكتبة لجلب المدخلات
# سنبسطها هنا لتعتمد على متغيرات البيئة التي يمررها الـ YAML

def get_video_data(url, category):
    scraper = cloudscraper.create_scraper()
    try:
        response = scraper.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # استخراج العنوان (من h1 أو og:title)
        title_raw = soup.find('h1').text.strip() if soup.find('h1') else "عنوان غير معروف"
        
        # استخراج البوستر
        img_tag = soup.find('meta', property='og:image')
        poster = img_tag['content'] if img_tag else "https://via.placeholder.com/300x450?text=No+Poster"
        
        # البحث عن رابط الفيديو (الآيفريم)
        # سنبحث عن أول iframe يحتوي على src
        iframe = soup.find('iframe')
        video_url = iframe['src'] if iframe else "#"

        # تنظيف العنوان (إزالة كلمة "حلقة" للحصول على اسم المسلسل)
        # نفترض أن العنوان: "ون بيس الحلقة 1100" -> المسلسل: "ون بيس"
        series_name = title_raw.split(" الحلقة")[0].split(" Episode")[0].strip()

        return {
            "series": series_name,
            "ep_name": title_raw,
            "poster": poster,
            "url": video_url,
            "category": category
        }
    except Exception as e:
        print(f"حدث خطأ أثناء السحب: {e}")
        return None

def update_db(data):
    scraper = cloudscraper.create_scraper()
    api_url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    # 1. جلب الملف الحالي
    res = scraper.get(api_url, headers=headers)
    if res.status_code != 200:
        print("فشل في الوصول للملف، ربما المسار خاطئ.")
        return

    file_info = res.json()
    db = json.loads(base64.b64decode(file_info['content']).decode('utf-8'))

    # 2. تحديث البيانات (نظام المكتبة)
    found = False
    for item in db:
        if item['title'] == data['series']:
            # إضافة الحلقة إذا لم تكن موجودة
            if not any(ep['url'] == data['url'] for ep in item['episodes']):
                item['episodes'].append({"name": data['ep_name'], "url": data['url']})
            found = True
            break
    
    if not found:
        db.append({
            "title": data['series'],
            "poster": data['poster'],
            "category": data['category'],
            "episodes": [{"name": data['ep_name'], "url": data['url']}]
        })

    # 3. حفظ ورفع الملف
    new_content = base64.b64encode(json.dumps(db, indent=2, ensure_ascii=False).encode('utf-8')).decode('utf-8')
    update_payload = {
        "message": f"إضافة: {data['ep_name']}",
        "content": new_content,
        "sha": file_info['sha']
    }
    
    final_res = scraper.put(api_url, headers=headers, json=update_payload)
    if final_res.status_code == 200:
        print(f"✅ تم إضافة {data['ep_name']} بنجاح!")
    else:
        print(f"❌ خطأ في الرفع: {final_res.text}")

# استدعاء القيم من Workflow Inputs (نحتاج لتعديل بسيط في كيفية قراءة الـ inputs)
if __name__ == "__main__":
    # بما أننا نستخدم workflow_dispatch، سنقرأ الملف الذي ينشئه GitHub للحدث
    event_path = os.getenv('GITHUB_EVENT_PATH')
    if event_path:
        with open(event_path, 'r') as f:
            event_data = json.load(f)
            url = event_data['inputs']['target_url']
            cat = event_data['inputs']['category']
            
            extracted = get_video_data(url, cat)
            if extracted:
                update_db(extracted)
