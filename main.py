

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import requests
import schedule 
import time
import random
import re


def human_delay(min_seconds=1, max_seconds=3.5):
    time.sleep(random.uniform(min_seconds, max_seconds))

def discord_alert(product_name, product_link):
    webhook_url = "https://discord.com/api/webhooks/1564150826291699836/IDR98QpaLU1j0tOefomea_hPXt6N9HpUowNdsMp6G4wHMcQ_W2JgpVQopD5jd_CR22pi"
    payload = {"content": f"🚨 **Real Match Found!** Stock match on Amazon.ca:\n`{product_name}`\n<{product_link}>"
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
        page.goto('https://www.amazon.ca/s?k=HUAWEI+WATCH+GT+7+Pro', timeout=60000)
        human_delay(2, 5)


        page_content = page.content().lower()
        if "api-services-support@amazon.com" in page_content or "enter the characters you see below" in page_content:
            print("blocked: Amazon served a CAPTCHA / Robot Check page.")
            browser.close()
            return

        results = page.locator('div[data-component-type="s-search-result"]')
        print(f"Scanning {results.count()} product result cards...")

        match_found = False
        for i in range(results.count()):
            card = results.nth(i)

            if card.locator('span:has-text("Sponsored")').count() > 0:
                continue
                
            title_element = card.locator('h2 a span')
            link_element = card.locator('h2 a')
            
            if title_element.count() > 0 and link_element.count() > 0:
                title = title_element.inner_text().strip()
                link = link_element.get_attribute('href')
                lower_title = title.lower()

                if link and "/dp/" in link:
                    if "huawei" in lower_title and "gt 7 pro" in lower_title:
                        if re.search(r'(https?://|t\.me/|telegram|join|tucos|a-tools|app|bot|channel)', lower_title):
                            print(f"Ignored spam pattern in title: {title}")
                            continue    
                    full_link = f"https://www.amazon.ca{link}"
                    print(f"REAL MATCH FOUND: {title}")
                    discord_alert(title, full_link)
                    match_found = True
                    break  
              
        if not match_found:
            print("No matching products found in this check cycle")
            
        browser.close()
        print("Check cycle complete. Browser closed")  


if __name__ == "__main__":
    run_amazon_check()
