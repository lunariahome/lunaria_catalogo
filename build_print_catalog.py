import json
import os
import math

def build_print_catalog():
    if not os.path.exists('products_db.json'):
        print("No se encontró products_db.json")
        return

    with open('products_db.json', 'r', encoding='utf-8') as f:
        products = json.load(f)

    # Filter out out-of-stock items if desired, but for now let's keep all or just the available ones.
    # Usually a printable catalog only shows available items.
    available_products = [p for p in products if p.get('stock_msg') != 'Agotado']

    html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Catálogo LUNARIA</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&family=Playfair+Display:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">
    <style>
        @page {
            size: A4;
            margin: 0;
        }
        body {
            margin: 0;
            padding: 0;
            font-family: 'Outfit', sans-serif;
            background-color: #fff;
            color: #3b302c;
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }
        .page {
            width: 210mm;
            height: 297mm;
            padding: 20mm;
            box-sizing: border-box;
            page-break-after: always;
            position: relative;
            background: #fff;
            overflow: hidden;
        }
        
        /* Portada */
        .cover {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            background: #fbf9f6;
        }
        .cover img {
            max-width: 300px;
            mix-blend-mode: multiply;
            margin-bottom: 20px;
        }
        .cover h1 {
            font-family: 'Playfair Display', serif;
            font-size: 3.5rem;
            margin: 0;
            font-weight: 600;
            letter-spacing: 3px;
            text-transform: uppercase;
            background: linear-gradient(135deg, #a67b4b, #d8ab76, #e9c996, #a67b4b);
            background-size: 200% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .cover p {
            font-size: 1.5rem;
            margin-top: 10px;
            color: #8b6b55;
            letter-spacing: 2px;
            text-transform: uppercase;
        }
        .cover .contact {
            margin-top: 50px;
            font-size: 1.2rem;
            color: #7a6e69;
        }
        .cover .contact a {
            color: #8b6b55;
            text-decoration: none;
            font-weight: 600;
        }
        .cover .contact a:hover {
            text-decoration: underline;
        }

        /* Header de las paginas internas */
        .page-header {
            text-align: center;
            margin-bottom: 15mm;
            border-bottom: 1px solid #e9c996;
            padding-bottom: 5mm;
        }
        .page-header h2 {
            font-family: 'Playfair Display', serif;
            font-size: 1.8rem;
            margin: 0;
            letter-spacing: 1px;
            text-transform: uppercase;
            background: linear-gradient(135deg, #a67b4b, #d8ab76, #e9c996, #a67b4b);
            background-size: 200% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        /* Grilla de 4 productos por página */
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            grid-template-rows: repeat(2, 1fr);
            gap: 15mm;
            height: 220mm; /* espacio restante */
        }
        
        .product {
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            background: #fbf9f6;
            border-radius: 12px;
            padding: 10mm;
            box-shadow: 0 4px 15px rgba(139, 107, 85, 0.05);
            border: 1px solid rgba(139, 107, 85, 0.1);
            overflow: hidden;
        }
        
        .product-img-wrapper {
            height: 55mm; /* Ajustado para que no se corte */
            width: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: 5mm;
        }
        
        .product img {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
            border-radius: 8px;
        }
        
        .product-title {
            font-family: 'Playfair Display', serif;
            font-size: 1.1rem;
            font-weight: 600;
            margin: 0 0 5px 0;
            line-height: 1.2;
            color: #3b302c;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

        .product-desc {
            font-size: 0.8rem;
            color: #7a6e69;
            margin: 0 0 10px 0;
            line-height: 1.3;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
            flex-grow: 1;
        }
        
        .product-price {
            font-size: 1.3rem;
            font-weight: 600;
            color: #8b6b55;
            margin-top: auto;
        }

        /* Footer de página */
        .page-footer {
            position: absolute;
            bottom: 10mm;
            left: 0;
            width: 100%;
            text-align: center;
            font-size: 0.85rem;
            color: #a67b4b;
        }
    </style>
</head>
<body>
    <!-- Portada -->
    <div class="page cover">
        <img src="logo.png" alt="LUNARIA">
        <h1>LUNARIA</h1>
        <p>Catálogo de Productos</p>
        <div class="contact">
            Instagram: <a href="https://instagram.com/_lunariahome_" target="_blank">@_lunariahome_</a><br>
            WhatsApp: <a href="https://wa.me/5493476355526" target="_blank">+54 9 3476 35-5526</a>
        </div>
    </div>
"""

    items_per_page = 4
    total_pages = math.ceil(len(available_products) / items_per_page)

    for i in range(total_pages):
        html += '    <div class="page">\n'
        html += '        <div class="page-header">\n'
        html += '            <h2>LUNARIA - Bazar y Deco</h2>\n'
        html += '        </div>\n'
        html += '        <div class="grid">\n'
        
        page_items = available_products[i * items_per_page : (i + 1) * items_per_page]
        for p in page_items:
            html += f'''            <div class="product">
                <div class="product-img-wrapper">
                    <img src="{p['img']}" alt="{p['name']}">
                </div>
                <h3 class="product-title">{p['name']}</h3>
                <p class="product-desc">{p.get('desc', '')}</p>
                <div class="product-price">{p['price']}</div>
            </div>\n'''
            
        html += '        </div>\n'
        html += '    </div>\n'

    html += """</body>
</html>
"""

    with open('catalog_print.html', 'w', encoding='utf-8') as f:
        f.write(html)
        
    print(f"Catálogo imprimible generado en catalog_print.html con {len(available_products)} productos.")

if __name__ == '__main__':
    build_print_catalog()
