from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import requests
import schedule 
import time
import random

def human_delay(min_seconds=1, max_seconds=3.5):
    time.sleep(random.uniform(min_seconds, max_seconds))

def discord_alert(product_name):
    webhook_url = "https://discord.com/api/webhooks/1564150826291699836/IDR98QpaLU1j0tOefomea_hPXt6N9HpUowNdsMp6G4wHMcQ_W2JgpVQopD5jd_CR22pi"
    payload = {"content": f"🚨 **Match Found!** Possible stock match on Amazon.ca:\n`{product_name}`"
           }
    try:
        response = requests.post(webhook_url, json=payload)
        if response.status_code == 204:
            print("Discord alert sent successfully!")
        else:
            print(f"Failed to send alert. Status code: {response.status_code}")
    except Exception as e:
        print(f"error sending Discord webhook: {e}")

def run_amazon_check():
    print("starting amazon check")     
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("Going to Amazon.ca")
        page.goto('https://www.amazon.ca')
        human_delay(2, 5)
        print("searching for HUAWEI WATCH GT 7 Pro")
        search_bar = page.locator('#twotabsearchtextbox')
        search_bar.fill('HUAWEI WATCH GT 7 Pro')
        search_bar.press('Enter')
        page.wait_for_load_state('networkidle')
        human_delay(2, 5)

        product_titles = page.locator('h2 a span').all_inner_texts()
    
        print(f"Scanning {len(product_titles)} results for matches")

        match_found = False
        for title in product_titles:
            lower_title = title.lower()
            
          
            if "huawei" in lower_title and "gt 7 pro" in lower_title:
                print(f"MATCH FOUND: {title}")
                discord_alert(title)
                match_found = True
                break  
        if not match_found:
            print("No matching products found in this check cycle")
            
        browser.close()
        print("Check cycle complete. Browser closed")  

schedule.every(4).hours.do(run_amazon_check)
run_amazon_check()

print("Scheduler active. Will run every 4 hours")
while True:
    schedule.run_pending()
    time.sleep(1)
