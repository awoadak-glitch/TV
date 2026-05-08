import requests
import time

# قائمة السيرفرات التي جمعتها (المصادر الأساسية)
PROVIDERS = [
    {"name": "VidLink (VIP)", "url": "https://vidlink.pro/embed/{type}/{id}?primaryColor=ff0000&autoplay=false"},
    {"name": "EmbedSU (Multi)", "url": "https://embed.su/embed/{type}/{id}"},
    {"name": "VidsrcTO (Stable)", "url": "https://vidsrc.to/embed/{type}/{id}"},
    {"name": "VidsrcME (Classic)", "url": "https://vidsrc.me/embed/{type}/{id}"},
    {"name": "VidsrcCC (Alt)", "url": "https://vidsrc.cc/v2/embed/{type}/{id}"}
]

def check_and_resolve(tmdb_id, media_type="movie"):
    """
    يقوم بتجربة السيرفرات واحداً تلو الآخر ويختار الأفضل
    """
    working_sources = []
    
    print(f"🔍 فحص السيرفرات لـ {media_type} ID: {tmdb_id}...")

    for source in PROVIDERS:
        test_url = source["url"].format(type=media_type, id=tmdb_id)
        
        try:
            # نقوم بإرسال طلب فحص سريع (Header request) للتأكد أن السيرفر ليس 404
            response = requests.head(test_url, timeout=5, allow_redirects=True)
            
            if response.status_code == 200:
                print(f"✅ {source['name']} يعمل!")
                working_sources.append({
                    "name": source["name"],
                    "url": test_url
                })
            else:
                print(f"❌ {source['name']} غير متاح حالياً (Status: {response.status_code})")
        except Exception as e:
            print(f"⚠️ خطأ في الاتصال بـ {source['name']}")
            
    return working_sources

# مثال للاستخدام في البوت:
# tmdb_id = "550" (فيلم Fight Club)
# results = check_and_resolve(tmdb_id)
