import math
import json
import os
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup

def format_manual_price(p):
    p_clean = str(p).replace('$', '').replace('.', '').replace(',', '.').strip()
    try:
        val = float(p_clean)
        return f"${int(val):,}".replace(',', '.')
    except:
        return f"${p}"

def calculate_markup(price_str, name=""):
    try:
        clean_str = price_str.replace('$', '').replace('.', '').replace(',', '.').strip()
        original_val = float(clean_str)
        val = original_val
        if val <= 3000:
            val += 2500
        elif val <= 7000:
            val = (val * 1.40)
        elif val <= 12000:
            val = (val * 1.40)
        elif val <= 17900:
            val = (val * 1.35)
        elif val <= 20000:
            val = (val * 1.30)
        elif val <= 25000:
            val = (val * 1.25)
        else:
            val = (val * 1.20)
            
        name_lower = name.lower()
        if 'camino' in name_lower:
            val += 4000
            
        val = math.ceil(val / 100.0) * 100
        
        # Override rules
        if 'alfombra' in name_lower and 'baño' in name_lower:
            if val == 9000:
                val = 10000
        elif 'alfombra' in name_lower:
            # Min profit 5500 for non-bath alfombras
            if (val - original_val) < 5500:
                val = original_val + 5500
                val = math.ceil(val / 100.0) * 100
        
        if 'manta' in name_lower:
            if (val - original_val) < 5500:
                val = original_val + 5500
                val = math.ceil(val / 100.0) * 100
                
        return f"${int(val):,}".replace(',', '.')
    except Exception as e:
        return price_str

logo_path = 'logo.png'

manual_prices = {}
if os.path.exists('manual_prices.json'):
    with open('manual_prices.json', 'r', encoding='utf-8') as f:
        manual_prices = json.load(f)

# Scrape all products from all pages
products = []
page = 1
while True:
    url = f'https://www.wearehome.com.ar/productos/?page={page}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        html = urllib.request.urlopen(req).read()
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.select('.item')
        if not items:
            break
            
        for item in items:
            name_el = item.select_one('.item-name')
            price_el = item.select_one('.item-price')
            img_el = item.select_one('img')
            a_el = item.select_one('a')
            if not (name_el and price_el): continue
            
            name = name_el.get('title') or name_el.get('aria-label') or name_el.text.strip()
            if name in manual_prices:
                price = format_manual_price(manual_prices[name])
            else:
                price = calculate_markup(price_el.text.strip(), name)
            
            link = a_el['href'] if a_el and a_el.has_attr('href') else ''
            if link and not link.startswith('http'):
                link = 'https://www.wearehome.com.ar' + link
            img = ''
            if img_el:
                if img_el.has_attr('data-srcset'):
                    srcset = img_el['data-srcset']
                    img = srcset.split(',')[0].split(' ')[0]
                    if img.startswith('//'):
                        img = 'https:' + img
                elif img_el.has_attr('src'):
                    img = img_el['src']
                    if img.startswith('//'):
                        img = 'https:' + img
            
            desc = f'Añade un toque único a tu hogar con {name}. Diseñado con materiales de alta calidad y un acabado excepcional para complementar cualquier estilo de decoración.'
            
            if 'camino' in name.lower() and link:
                try:
                    import re
                    req_detail = urllib.request.Request(link, headers={'User-Agent': 'Mozilla/5.0'})
                    html_detail = urllib.request.urlopen(req_detail, timeout=5).read()
                    soup_detail = BeautifulSoup(html_detail, 'html.parser')
                    desc_el = soup_detail.select_one('.product-description')
                    if desc_el:
                        m = re.search(r'(\d+\s*[xX]\s*\d+)', desc_el.text, re.IGNORECASE)
                        if m:
                            desc += f' Medida: {m.group(1)}cm.'
                except Exception:
                    pass
            
            stock_msg = ''
            stock_el = item.select_one('.js-stock-label')
            if stock_el:
                style = stock_el.get('style', '').replace(' ', '').lower()
                if 'display:none' not in style:
                    msg = stock_el.text.strip()
                    if msg:
                        stock_msg = msg
                    elif stock_el.has_attr('data-label') and stock_el['data-label']:
                        stock_msg = stock_el['data-label']
            
            # Tiendanube also shows "pocas unidades" in some tags if configured
            
            products.append({
                'name': name,
                'price': price,
                'original_price': price_el.text.strip(),
                'img': img,
                'desc': desc,
                'stock_msg': stock_msg,
                'link': link
            })
            
        print(f'Scraped page {page} ({len(items)} items)')
        page += 1

    except Exception as e:
        print(f'Error scraping page {page}: {e}')
        break

seen = set()
unique_products = []
for p in products:
    if p['name'] not in seen:
        seen.add(p['name'])
        unique_products.append(p)

# Filtered categories
categories_data = [
    {"name": "Todos los productos", "keywords": [""]},
    {
        "name": "Alfombras", 
        "keywords": ["alfombra"],
        "subcategories": [
            {"name": "Yute", "keywords": ["yute"]},
            {"name": "Felpudos", "keywords": ["felpudo"]},
            {"name": "Baño", "keywords": ["baño"]},
            {
                "name": "Algodón", 
                "keywords": ["algodon"],
                "subcategories": [
                    {"name": "Cuyo", "keywords": ["cuyo"]},
                    {"name": "Alfombras mantas rusticas", "keywords": ["mantas rusticas", "rustica"]},
                    {"name": "Onairuyamolly", "keywords": ["onair", "uya", "molly", "onairuyamolly"]},
                    {"name": "Estampadas", "keywords": ["estampada"]},
                    {"name": "Otras", "keywords": []}
                ]
            }
        ]
    },
    {"name": "Cortinas", "keywords": ["cortina"]},
    {"name": "Bolsos / Necessaire", "keywords": ["bolso", "necessaire"]},
    {"name": "Contenedores / Cestos de ropa", "keywords": ["contenedor", "cesto"]},
    {
        "name": "Almohadones", 
        "keywords": ["almohadon", "almohadón"],
        "subcategories": [
            {
                "name": "Fundas", 
                "keywords": ["funda"],
                "subcategories": [
                    {"name": "50x50", "keywords": ["50x50"]},
                    {"name": "50x70", "keywords": ["50x70"]},
                    {"name": "60x34", "keywords": ["60x34", "60x35"]},
                    {"name": "Rectangulares chicos", "keywords": ["rectangular chico", "rectangulares chicos"]}
                ]
            },
            {"name": "Rellenos", "keywords": ["relleno"]},
            {"name": "Completos", "keywords": ["completo"]}
        ]
    },
    {"name": "Mantas", "keywords": ["manta"]},
    {
        "name": "Para la cama", 
        "keywords": ["cama", "acolchado", "cubrecama", "pie de cama", "sommier", "frazada"],
        "subcategories": [
            {"name": "Acolchados", "keywords": ["acolchado"]},
            {"name": "Cubrecamas", "keywords": ["cubrecama"]},
            {"name": "Pie de cama", "keywords": ["pie de cama"]},
            {"name": "Cubre sommier", "keywords": ["sommier"]},
            {"name": "Frazadas", "keywords": ["frazada"]}
        ]
    },
    {
        "name": "Para la mesa", 
        "keywords": ["mesa", "mantel", "camino", "servilleta", "porta cubierto", "paño", "plato de sitio"],
        "subcategories": [
            {"name": "Manteles", "keywords": ["mantel"]},
            {"name": "Caminos de mesa", "keywords": ["camino de mesa", "caminos de mesa", "camino"]},
            {"name": "Servilletas", "keywords": ["servilleta"]},
            {"name": "Paños", "keywords": ["paño"]},
            {"name": "Porta cubiertos", "keywords": ["porta cubierto", "porta cubiertos"]}
        ]
    },
    {"name": "Almohadones para sillas", "keywords": ["silla"]},
    {"name": "Para la cocina", "keywords": ["cocina"]},
    {"name": "Lonas", "keywords": ["lona"]},
    {"name": "Toallas", "keywords": ["toalla", "toallon"]},
    {"name": "Trapitos de piso", "keywords": ["trapito", "piso"]},
    {"name": "Traba puertas / Stop Door", "keywords": ["traba", "door"]},
    {"name": "Mascotas", "keywords": ["mascota", "perro", "gato"]},
    {"name": "Pillows", "keywords": ["pillow"]},
    {"name": "Mundial", "keywords": ["mundial"]},
    {"name": "Invierno", "keywords": ["invierno"]}
]

def build_menu_html(categories, level=0):
    html = ""
    padding = 25 + (level * 15)
    for c in categories:
        kws = ",".join(c["keywords"])
        if "subcategories" in c:
            html += f'''
            <details class="menu-details">
                <summary class="menu-item" style="padding-left: {padding}px">{c["name"]}</summary>
                <div class="submenu">
                    <a href="#" class="menu-item sub" style="padding-left: {padding + 15}px" onclick="filterProducts(event, '{kws}')">Ver todo: {c["name"]}</a>
                    {build_menu_html(c["subcategories"], level + 1)}
                </div>
            </details>
            '''
        else:
            html += f'<a href="#" class="menu-item" style="padding-left: {padding}px" onclick="filterProducts(event, \'{kws}\')">{c["name"]}</a>'
    return html

cat_html = build_menu_html(categories_data)

html_template = f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Catálogo LUNARIA bazar y deco</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&family=Playfair+Display:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #fbf9f6;
            --text-color: #3b302c;
            --accent-color: #8b6b55;
            --white: #ffffff;
            --card-shadow: 0 10px 30px rgba(139, 107, 85, 0.08);
            --hover-shadow: 0 15px 40px rgba(139, 107, 85, 0.15);
        }}
        body {{
            font-family: 'Outfit', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 0;
        }}
        .top-bar {{
            background: linear-gradient(135deg, #a67b4b, #d8ab76, #e9c996, #a67b4b);
            background-size: 200% auto;
            color: var(--white);
            text-align: center;
            padding: 10px;
            font-size: 0.9rem;
            letter-spacing: 1px;
        }}
        .top-bar a {{
            color: var(--white);
            text-decoration: none;
            font-weight: 600;
        }}
        .top-bar a:hover {{
            text-decoration: underline;
        }}
        header {{
            background-color: var(--white);
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.03);
            position: relative;
        }}
        .logo {{
            max-width: 200px;
            /* mix-blend-mode multiply removes the white background effectively */
            mix-blend-mode: multiply;
        }}
        .header-title {{
            font-family: 'Playfair Display', serif;
            font-size: 2.5rem;
            margin-top: 5px;
            margin-bottom: 0;
            font-weight: 600;
            letter-spacing: 2px;
            text-transform: uppercase;
            background: linear-gradient(135deg, #a67b4b, #d8ab76, #e9c996, #a67b4b);
            background-size: 200% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .header-subtitle {{
            font-family: 'Outfit', sans-serif;
            font-size: 1.1rem;
            margin-top: -5px;
            margin-bottom: 0;
            font-weight: 400;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            background: linear-gradient(135deg, #a67b4b, #d8ab76, #e9c996, #a67b4b);
            background-size: 200% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .stock-badge {{
            position: absolute;
            top: 15px;
            right: 15px;
            background-color: rgba(255, 255, 255, 0.9);
            color: #d15151;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            letter-spacing: 0.5px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            z-index: 10;
        }}
        
        /* Collapsible Menu Styles */
        .menu-toggle {{
            position: absolute;
            top: 30px;
            left: 20px;
            background: none;
            border: none;
            cursor: pointer;
            display: flex;
            flex-direction: column;
            gap: 6px;
            z-index: 200;
        }}
        .menu-toggle span {{
            display: block;
            width: 30px;
            height: 3px;
            background-color: var(--accent-color);
            border-radius: 2px;
            transition: all 0.3s;
        }}
        .side-menu {{
            position: fixed;
            top: 0;
            left: -300px;
            width: 250px;
            height: 100vh;
            background-color: var(--white);
            box-shadow: 5px 0 15px rgba(0,0,0,0.1);
            transition: left 0.3s ease;
            z-index: 1000;
            overflow-y: auto;
            padding-top: 60px;
        }}
        .side-menu.open {{
            left: 0;
        }}
        .close-menu {{
            position: absolute;
            top: 20px;
            right: 20px;
            font-size: 1.5rem;
            color: var(--accent-color);
            cursor: pointer;
            background: none;
            border: none;
        }}
        .menu-item {{
            display: block;
            padding: 15px 25px;
            color: var(--text-color);
            text-decoration: none;
            font-size: 1.1rem;
            border-bottom: 1px solid rgba(139, 107, 85, 0.1);
            transition: background-color 0.2s, color 0.2s;
        }}
        .menu-item:hover {{
            background-color: var(--bg-color);
            color: var(--accent-color);
        }}
        .menu-details summary {{
            cursor: pointer;
            list-style: none;
            position: relative;
        }}
        .menu-details summary::-webkit-details-marker {{
            display: none;
        }}
        .menu-details summary::after {{
            content: '+';
            position: absolute;
            right: 20px;
            font-size: 1.2rem;
            color: var(--accent-color);
        }}
        .menu-details[open] > summary::after {{
            content: '-';
        }}
        .submenu {{
            background-color: #faf7f2;
            border-left: 2px solid rgba(139, 107, 85, 0.2);
            margin-left: 10px;
        }}
        .menu-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background-color: rgba(0,0,0,0.4);
            display: none;
            z-index: 999;
        }}
        .menu-overlay.show {{
            display: block;
        }}

        .container {{
            max-width: 1400px;
            margin: 50px auto;
            padding: 0 20px;
        }}
        .catalog-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 40px;
        }}
        .product-card {{
            background-color: var(--white);
            border-radius: 16px;
            overflow: hidden;
            box-shadow: var(--card-shadow);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            display: flex;
            flex-direction: column;
            border: 1px solid rgba(139, 107, 85, 0.05);
        }}
        .product-card:hover {{
            transform: translateY(-10px);
            box-shadow: var(--hover-shadow);
        }}
        .image-container {{
            position: relative;
            width: 100%;
            padding-top: 100%;
            overflow: hidden;
            background-color: #f5f2ed;
        }}
        .product-image {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.6s ease;
        }}
        .product-card:hover .product-image {{
            transform: scale(1.05);
        }}
        .product-info {{
            padding: 30px;
            display: flex;
            flex-direction: column;
            flex-grow: 1;
        }}
        .product-title {{
            font-family: 'Playfair Display', serif;
            font-size: 1.4rem;
            font-weight: 600;
            margin: 0 0 15px 0;
            line-height: 1.3;
            color: var(--text-color);
        }}
        .product-desc {{
            font-size: 0.95rem;
            color: #7a6e69;
            line-height: 1.6;
            margin-bottom: 25px;
            flex-grow: 1;
        }}
        .product-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: auto;
            padding-top: 20px;
            border-top: 1px solid rgba(139, 107, 85, 0.1);
        }}
        .product-price {{
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--accent-color);
        }}
        .btn-buy {{
            background-color: var(--accent-color);
            color: var(--white);
            border: none;
            padding: 12px 25px;
            border-radius: 30px;
            font-family: 'Outfit', sans-serif;
            font-weight: 600;
            font-size: 0.95rem;
            cursor: pointer;
            transition: background-color 0.3s ease, transform 0.2s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            text-decoration: none;
            text-align: center;
        }}
        .btn-buy:hover {{
            background-color: #705543;
            transform: translateY(-2px);
        }}
        .cart-icon {{
            position: absolute;
            right: 20px;
            top: 25px;
            font-size: 1.8rem;
            cursor: pointer;
            color: var(--accent-color);
        }}
        #cart-count {{
            position: absolute;
            top: -8px;
            right: -10px;
            background: #d32f2f;
            color: white;
            border-radius: 50%;
            padding: 2px 6px;
            font-size: 0.8rem;
            font-weight: bold;
        }}
        .cart-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }}
        .cart-item-info {{
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        .cart-item img {{
            width: 50px;
            height: 50px;
            object-fit: cover;
            border-radius: 8px;
        }}
        .cart-item-title {{
            font-size: 0.95rem;
            font-weight: 600;
            color: var(--text-color);
        }}
        .cart-item-price {{
            font-size: 0.9rem;
            color: var(--accent-color);
        }}
        .btn-remove {{
            background: none;
            border: none;
            color: #d32f2f;
            cursor: pointer;
            font-size: 1.2rem;
        }}

        #toast {{
            visibility: hidden;
            min-width: 250px;
            background-color: var(--accent-color);
            color: #fff;
            text-align: center;
            border-radius: 8px;
            padding: 16px;
            position: fixed;
            z-index: 4000;
            left: 50%;
            bottom: 30px;
            transform: translateX(-50%);
            font-size: 1rem;
            font-family: 'Outfit', sans-serif;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
            opacity: 0;
            transition: opacity 0.3s, bottom 0.3s;
        }}
        #toast.show {{
            visibility: visible;
            opacity: 1;
            bottom: 50px;
        }}

        .input-name {{
            width: 100%;
            padding: 12px;
            border: 1px solid #ccc;
            border-radius: 8px;
            margin-top: 15px;
            font-size: 1rem;
            font-family: 'Outfit', sans-serif;
            box-sizing: border-box;
        }}

        @media (max-width: 768px) {{
            .catalog-grid {{
                grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
                gap: 25px;
            }}
            .header-title {{
                font-size: 2rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="menu-overlay" id="welcome-overlay" style="display: flex; justify-content: center; align-items: center; z-index: 2000;">
        <div style="background: var(--white); padding: 40px; border-radius: 16px; text-align: center; max-width: 400px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); position: relative;">
            <button onclick="document.getElementById('welcome-overlay').style.display='none'" style="position: absolute; top: 15px; right: 15px; background: none; border: none; font-size: 1.5rem; color: var(--accent-color); cursor: pointer;">&times;</button>
            <h2 style="font-family: 'Playfair Display', serif; color: var(--accent-color); margin-bottom: 20px;">Bienvenido a LUNARIA</h2>
            <p style="font-size: 1.1rem; line-height: 1.5; color: var(--text-color);">Recordá que trabajamos por encargue y el pedido se toma con una seña del 50%.</p>
            <button onclick="document.getElementById('welcome-overlay').style.display='none'" class="btn-buy" style="margin-top: 25px; width: 100%;">Entendido</button>
        </div>
    </div>

    <div class="top-bar">
        Síguenos en Instagram: <a href="https://instagram.com/_lunariahome_" target="_blank">@_lunariahome_</a>
    </div>
    <header>
        <button class="menu-toggle" id="menu-btn" aria-label="Menú">
            <span></span>
            <span></span>
            <span></span>
        </button>
        <img src="{logo_path}" alt="LUNARIA bazar y deco" class="logo">
        <h1 class="header-title">LUNARIA</h1>
        <p class="header-subtitle">bazar y deco</p>
        <div class="cart-icon" onclick="openCart()">
            🛒 <span id="cart-count">0</span>
        </div>
    </header>


    <div class="menu-overlay" id="overlay"></div>
    <div class="side-menu" id="side-menu">
        <button class="close-menu" id="close-btn">&times;</button>
        <h3 style="padding: 0 25px; color: var(--accent-color); font-family: 'Playfair Display', serif;">Categorías</h3>
        {cat_html}
    </div>
    
    <div class="container">
        <div class="catalog-grid">
'''

for p in unique_products:
    if p['name'] and p['price']:
        stock_html = f'<div class="stock-badge">{p["stock_msg"]}</div>' if p.get('stock_msg') else ''
        p_name_esc = p['name'].replace("'", "\'")
        p_img = p['img']
        p_price = p['price']
        
        html_template += f'''
            <div class="product-card" data-title="{p['name'].lower().replace('"', '')}">
                <div class="image-container">
                    {stock_html}
                    <img src="{p_img}" alt="{p['name']}" class="product-image" loading="lazy">
                </div>
                <div class="product-info">
                    <h2 class="product-title">{p['name']}</h2>
                    <p class="product-desc">{p['desc']}</p>
                    <div class="product-footer">
                        <span class="product-price">{p_price}</span>
                        <div style="display:flex; gap: 8px;">
                            <button onclick="addToCart('{p_name_esc}', '{p_price}', '{p_img}')" class="btn-buy" style="padding: 12px; background: var(--secondary-color); color: var(--accent-color); font-size: 1.2rem;" title="Agregar al carrito">🛒</button>
                            <button onclick="buySingle('{p_name_esc}', '{p_price}')" class="btn-buy">Lo quiero</button>
                        </div>
                    </div>
                </div>
            </div>
'''


html_template += '''

        </div>
    </div>
    

    <!-- Toast Notification -->
    <div id="toast">Producto agregado al carrito ✅</div>

    <!-- Modal Nombre -->
    <div class="menu-overlay" id="name-modal" style="display: none; justify-content: center; align-items: center; z-index: 3000;">
        <div style="background: var(--white); padding: 30px; border-radius: 16px; width: 90%; max-width: 400px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); position: relative;">
            <button onclick="closeNameModal()" style="position: absolute; top: 15px; right: 15px; background: none; border: none; font-size: 1.5rem; color: var(--accent-color); cursor: pointer;">&times;</button>
            <h2 style="font-family: 'Playfair Display', serif; color: var(--accent-color); margin-bottom: 10px; text-align: center;">Tus datos</h2>
            <p style="font-size: 0.95rem; color: var(--text-color); text-align: center;">Ingresá tu nombre y apellido para enviarnos el pedido por WhatsApp.</p>
            <input type="text" id="user-name-input" class="input-name" placeholder="Ej. María Pérez">
            <button onclick="submitName()" class="btn-buy" style="margin-top: 20px; width: 100%;">Continuar a WhatsApp</button>
        </div>
    </div>

    <!-- Modal Carrito -->
    <div class="menu-overlay" id="cart-modal" style="display: none; justify-content: center; align-items: center; z-index: 3000;">
        <div style="background: var(--white); padding: 30px; border-radius: 16px; width: 90%; max-width: 500px; max-height: 80vh; overflow-y: auto; box-shadow: 0 10px 40px rgba(0,0,0,0.2); position: relative;">
            <button onclick="closeCart()" style="position: absolute; top: 15px; right: 15px; background: none; border: none; font-size: 1.5rem; color: var(--accent-color); cursor: pointer;">&times;</button>
            <h2 style="font-family: 'Playfair Display', serif; color: var(--accent-color); margin-bottom: 20px; text-align: center;">Tu Carrito 🛒</h2>
            
            <div id="cart-items-container">
                <!-- Javascript will populate this -->
            </div>
            
            <div style="margin-top: 20px; padding-top: 20px; border-top: 2px solid var(--secondary-color); display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 1.2rem; font-family: 'Playfair Display', serif; color: var(--accent-color); font-weight: bold;">Total:</span>
                <span id="cart-total-price" style="font-size: 1.5rem; font-weight: bold; color: var(--text-color);">$0</span>
            </div>
            <button onclick="buyCart()" class="btn-buy" style="margin-top: 20px; width: 100%;">Pedir Carrito por WhatsApp</button>
        </div>
    </div>
    
    <script>

        const menuBtn = document.getElementById('menu-btn');
        const closeBtn = document.getElementById('close-btn');
        const sideMenu = document.getElementById('side-menu');
        const overlay = document.getElementById('overlay');

        function toggleMenu() {
            sideMenu.classList.toggle('open');
            overlay.classList.toggle('show');
        }

        menuBtn.addEventListener('click', toggleMenu);
        closeBtn.addEventListener('click', toggleMenu);
        overlay.addEventListener('click', toggleMenu);

        function filterProducts(event, keywordStr) {
            event.preventDefault();
            const keywords = keywordStr.split(',');
            const cards = document.querySelectorAll('.product-card');
            cards.forEach(card => {
                const title = card.getAttribute('data-title');
                if (keywords.length === 1 && keywords[0] === "") {
                    card.style.display = 'flex';
                    return;
                }
                let show = false;
                for (let kw of keywords) {
                    if (title.includes(kw)) {
                        show = true;
                        break;
                    }
                }
                card.style.display = show ? 'flex' : 'none';
            });
            toggleMenu();
        }
    </script>
</body>
</html>
'''

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

with open('products_db.json', 'w', encoding='utf-8') as f:
    json.dump(unique_products, f, ensure_ascii=False, indent=2)

print(f'Generated catalog and DB with {len(unique_products)} products.')
