import urllib.request
from bs4 import BeautifulSoup
url = "https://www.wearehome.com.ar/productos/almohadon-completo-raya-ancha-azul-40x40cm-1ig9o/"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req, timeout=10).read()
soup = BeautifulSoup(html, 'html.parser')
desc_el = soup.select_one('.product-description')
if desc_el:
    print(repr(desc_el.get_text(separator='\n').strip()))
