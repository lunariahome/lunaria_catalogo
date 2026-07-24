import json
import urllib.request
import urllib.error
import time
from bs4 import BeautifulSoup
import re
import sys

def format_desc(text):
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    return text

def main():
    try:
        with open('products_db.json', 'r', encoding='utf-8') as f:
            products = json.load(f)
    except Exception as e:
        print("Error reading db:", e)
        return

    updated = 0
    total = len(products)
    
    print(f"Starting update of {total} products...")
    
    for i, p in enumerate(products):
        if 'Añade un toque único' not in p.get('desc', ''):
            continue
            
        link = p.get('link')
        if not link:
            continue
            
        success = False
        for attempt in range(5):
            try:
                req = urllib.request.Request(link, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
                html = urllib.request.urlopen(req, timeout=10).read()
                soup = BeautifulSoup(html, 'html.parser')
                desc_el = soup.select_one('.product-description')
                
                if desc_el:
                    new_desc = format_desc(desc_el.get_text(separator=' '))
                    if new_desc:
                        p['desc'] = new_desc
                else:
                    p['desc'] = p['name'] # Fallback
                    
                success = True
                break
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    print(f"Rate limited on {i}/{total}. Sleeping {2 * (attempt+1)}s...")
                    time.sleep(2 * (attempt + 1))
                else:
                    print(f"HTTP error {e.code} on {link}")
                    break
            except Exception as e:
                print(f"Error on {link}: {e}")
                break
                
        if success:
            updated += 1
            if updated % 5 == 0:
                print(f"Updated {updated} descriptions (Progress: {i}/{total})")
                with open('products_db.json', 'w', encoding='utf-8') as f:
                    json.dump(products, f, ensure_ascii=False, indent=2)
            time.sleep(0.5)
        else:
            print(f"Failed to fetch {link} after retries")
            
    with open('products_db.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
        
    print(f"Finished updating {updated} descriptions.")
    
if __name__ == '__main__':
    main()
