import json
import re
import socket
import time
import urllib.parse
import requests

# مصادر نشطة ومتجددة تنشر روابط بروكسيات MTProto
SOURCES = [
    "https://raw.githubusercontent.com/ALIILAPRO/MTProtoProxy/main/mtproto.txt",
    "https://raw.githubusercontent.com/SoliSpirit/mtproto/master/all_proxies.txt",
    "https://raw.githubusercontent.com/soroushmirzaei/telegram-proxies-collector/main/proxies"
]

def test_proxy(server, port):
    """فحص سرعة استجابة البروكسي"""
    try:
        start_time = time.time()
        sock = socket.create_connection((server, int(port)), timeout=3)
        sock.close()
        latency = int((time.time() - start_time) * 1000)
        return True, latency
    except Exception:
        return False, 0

def extract_proxies_from_text(text):
    """استخراج السيرفر والبورت والسيكرت من أي رابط تيليجرام"""
    extracted = []
    # البحث عن روابط https://t.me/proxy أو tg://proxy
    pattern = re.compile(r'(?:https?://t\.me/proxy|tg://proxy)\?([^\s"\'<>]+)')
    matches = pattern.findall(text)
    
    for query in matches:
        params = urllib.parse.parse_qs(query)
        server = params.get('server', [None])[0]
        port = params.get('port', [None])[0]
        secret = params.get('secret', [None])[0]
        if server and port and secret and port.isdigit():
            extracted.append((server, int(port), secret))
    return extracted

def harvest_proxies():
    raw_proxies = set()
    
    for src in SOURCES:
        try:
            print(f"Fetching from: {src}")
            res = requests.get(src, timeout=10)
            if res.status_code == 200:
                found = extract_proxies_from_text(res.text)
                for item in found:
                    raw_proxies.add(item)
        except Exception as e:
            print(f"Error fetching {src}: {e}")

    print(f"Found {len(raw_proxies)} unique proxies. Testing speed...")
    
    valid_proxies = []
    # فحص أول 60 بروكسي لتسريع العملية
    for server, port, secret in list(raw_proxies)[:60]:
        is_working, latency = test_proxy(server, port)
        if is_working:
            valid_proxies.append({
                "server": server,
                "port": port,
                "secret": secret,
                "latency": latency
            })

    # ترتيب البروكسيات من الأسرع إلى الأبطأ
    valid_proxies.sort(key=lambda x: x["latency"])

    # حفظ أفضل 15 بروكسي
    final_list = valid_proxies[:15]
    with open("proxies.json", "w", encoding="utf-8") as f:
        json.dump(final_list, f, indent=4)
    
    print(f"Saved {len(final_list)} working proxies to proxies.json")

if __name__ == "__main__":
    harvest_proxies()