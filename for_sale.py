from playwright.sync_api import sync_playwright
import random
import time
import pandas as pd
import re
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    filename='property_scrape.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

the_user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.92 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 15; Pixel 9 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.104 Mobile Safari/537.36",
]

def goto_with_retry(page, url, retries=3):
    for attempts in range(retries):
        try:
            page.goto(url,wait_until='domcontentloaded',timeout=60000)
            return True
        except Exception as e:
            if attempts < retries - 1:
                time.sleep(2 * (attempts + 1))
            else:
                logging.error(f'Failed to load {url} after {retries}: {e}')
                return False

def search_filter(listing_type, city, bedroom_num):
     return f'{listing_type}/{city}?bedrooms={bedroom_num}'

def property_scrape(headless, slow_mo, max_page, base_url, search_path):
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless,slow_mo=slow_mo)
        context = browser.new_context(user_agent=random.choice(the_user_agents))
        page = context.new_page()

        for i in range(1,max_page+1):
            url = f'{base_url}{search_path}&page={i}'
            logging.info(f'Scraping page {i}...')

            success = goto_with_retry(page, url)
            if not success:
                logging.info(f'Skipping page {i}')
                continue

            page.locator('div.wp-block.property.list').first.wait_for(state='visible')
            contents = page.locator('div.wp-block.property.list')
            count = contents.count()

            for c in range(count):
                content = contents.nth(c)
                content.wait_for(state='visible')
                
                try:
                    href = content.locator('div.wp-block-title a').first.get_attribute('href')
                    if href:
                        url_link = base_url.rstrip('/') + href
                    else:
                        url_link = 'N/A'
                except Exception as e:
                    logging.error(f'Error extracting link: {e}')
                    url_link = 'N/A'

                try:
                    title = content.locator('div.wp-block-title').inner_text()
                except Exception as e:
                    logging.error(f'Error extracting title: {e}')
                    title = "N/A"
                try:
                    address = content.locator('address').inner_text().strip()
                except Exception as e:
                    logging.error(f'Error extracting address: {e}')
                    address = "N/A"
                try:
                    price = "".join(content.locator('span.price').all_inner_texts())
                except Exception as e:
                    logging.error(f'Error extracting price: {e}')
                    price = "N/A"
                try:
                    agent_info = content.locator('span.marketed-by').inner_text().strip()
                except Exception as e:
                    logging.error(f'Error extracting agent info: {e}')
                    agent_info = "N/A"

                try:
                    content.locator("div.wp-block-footer").wait_for(state="visible")
                    footer_items = content.locator("div.wp-block-footer li")
                    count_footer = footer_items.count()

                    bedroom = bathroom = toilet = parking_space = sqm = 'N/A'

                    for f in range(count_footer):
                        try:
                            li = footer_items.nth(f)
                            spans = li.locator("span")
                            if spans.count() < 2:
                                continue

                            value = spans.nth(0).inner_text().strip()
                            label = spans.nth(1).inner_text().strip().lower()

                            if "bed" in label:
                                bedroom = value
                            elif "bath" in label:
                                bathroom = value
                            elif "toilet" in label:
                                toilet = value
                            elif "park" in label:
                                parking_space = value
                            elif "sqm" in label or "area" in label:
                                sqm = value

                        except Exception as e:
                            logging.error(f"Error extracting footer item {f}: {e}")
                except Exception as e:
                    logging.error(f"Error extracting footer block: {e}")
                    bedroom = bathroom = toilet = parking_space = sqm = 'N/A'

                date_scraped = datetime.now().strftime('%Y-%m-%d')

                results.append({
                    'Title': title,
                    'Address': address,
                    'Price': price,
                    'Agent_Info': agent_info, 
                    'Bedroom': bedroom,
                    'Bathroom': bathroom,
                    'Toilet': toilet,
                    'Parking_Space': parking_space,
                    'SQM': sqm,
                    'Link': url_link,
                    'Date': date_scraped
                })

                page.wait_for_timeout(random.randint(1000,1800))

        browser.close()
    
    logging.info(f'Total records scraped: {len(results)}')
    return results

if __name__ == "__main__":
    headless = False
    slow_mo = 500
    max_page = 5
    base_url = 'https://nigeriapropertycentre.com/'
    listing_type = 'for-sale'
    city = 'lagos'
    bedroom_num = 3

    search_path = search_filter(listing_type, city, bedroom_num)

    property_data = property_scrape(
        headless=headless,
        slow_mo=slow_mo,
        max_page=max_page,
        base_url= base_url,
        search_path = search_path
    )

    df = pd.DataFrame(property_data)
    df['Price_numeric'] = df['Price'].str.replace(r'[^\d.]', '', regex=True).replace('', '0').astype(int)
    df['Agent_Info'] = df['Agent_Info'].str.replace('\xa0', ' ', regex=False).str.replace(r'\s+', ' ', regex=True).str.strip()

    def mask_phone_numbers(text):
        text = str(text).strip()
        def replacer(match):
            number = match.group()
            return number[:-6] + "******"
        return re.sub(r'(\+?\d[\d\s]{9,})', replacer, text)

    df['Agent_Info'] = df['Agent_Info'].apply(mask_phone_numbers)

    df.head(10).to_csv('property_listings_sample.csv', index=False)