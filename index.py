# FILE: indexer.py
# ROLE: Force Google to index the new URL immediately via Indexing API.

import os
import json
import requests
from oauth2client.service_account import ServiceAccountCredentials

# إعداد دالة لوج (Log) بسيطة لتعويض الملف الخارجي إذا لم يكن موجوداً
def log(message):
    print(message)

SCOPES = ["https://www.googleapis.com/auth/indexing"]
ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"

def get_credentials():
    # يستخرج محتوى ملف الـ JSON من متغيرات البيئة في GitHub Actions
    json_creds = os.getenv('GOOGLE_INDEXING_JSON')
    if not json_creds:
        log("⚠️ Indexing Skipped: GOOGLE_INDEXING_JSON not found.")
        return None
    
    try:
        info = json.loads(json_creds)
        return ServiceAccountCredentials.from_json_keyfile_dict(info, SCOPES)
    except Exception as e:
        log(f"❌ Indexing Auth Error: {e}")
        return None

def submit_url(url):
    log(f"   🚀 [Indexer] Pinging Google for: {url}...")
    creds = get_credentials()
    if not creds: return

    try:
        access_token = creds.get_access_token().access_token
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        
        content = {
            "url": url,
            "type": "URL_UPDATED"
        }
        
        r = requests.post(ENDPOINT, data=json.dumps(content), headers=headers)
        
        if r.status_code == 200:
            log(f"      ✅ Google Indexing API: Success for {url}")
        else:
            log(f"      ⚠️ Indexing API Failed for {url}: {r.text}")
            
    except Exception as e:
        log(f"      ❌ Indexing Error for {url}: {e}")

def main():
    # مسار ملف الروابط الذي ستقوم صفحة الويب بتحديثه
    urls_file = "urls.txt"
    
    if not os.path.exists(urls_file):
        log(f"❌ Error: {urls_file} not found. Nothing to index.")
        return

    # قراءة الروابط وتنظيفها
    with open(urls_file, "r") as f:
        urls = [line.strip() for line in f if line.strip().startswith("http")]

    if not urls:
        log("⚠️ No valid URLs found in urls.txt.")
        return

    log(f"📂 Found {len(urls)} URLs to process...")
    
    # إرسال كل رابط إلى Google Indexing API
    for url in urls:
        submit_url(url)
        
    log("🏁 All indexing requests processed.")

if __name__ == "__main__":
    main()
