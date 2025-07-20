from flask import Flask
from threading import Thread
import time
import requests
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

app = Flask("")

@app.route('/')
def home():
    return "✅ Bot çalışıyor!"

def telegram_mesaj_gonder(token, chat_id, mesaj):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": mesaj, "parse_mode": "HTML"}
    return requests.post(url, data=data)

def scrape_oda_bildirimleri():
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.kap.org.tr/tr/bildirim-sorgu-sonuc?srcbar=Y&cmp=Y&cat=6&slf=ALL")
        page.wait_for_selector("table tbody tr", timeout=15000)
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")
    for row in soup.select("table tbody tr"):
        cols = row.find_all("td")
        if len(cols) >= 4 and "ÖDA" in cols[2].get_text(strip=True):
            results.append({
                "başlık": cols[3].get_text(strip=True),
                "link": cols[3].find("a")["href"]
            })
    return results

def loop_scraper():
    TOKEN = "7033994518:AAEmD3Kg1w2YAahYGNxXjkIkXV7j4Fh-Ksw"
    CHAT_ID = "1458759498"
    sent_links = set()

    while True:
        try:
            bildirimler = scrape_oda_bildirimleri()
            for b in bildirimler:
                if b["link"] not in sent_links:
                    mesaj = f"📢 <b>{b['başlık']}</b>\n🔗 https://www.kap.org.tr{b['link']}"
                    telegram_mesaj_gonder(TOKEN, CHAT_ID, mesaj)
                    sent_links.add(b["link"])
            time.sleep(3600)  # 1 saatte bir kontrol
        except Exception as e:
            print("Hata:", e)
            time.sleep(300)

def run_bot():
    t = Thread(target=loop_scraper)
    t.start()

def run_server():
    app.run(host="0.0.0.0", port=8080)

Thread(target=run_bot).start()
run_server()
