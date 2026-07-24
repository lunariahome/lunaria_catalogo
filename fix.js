const fs = require('fs');
let code = fs.readFileSync('build_catalog.py', 'utf8');

// Fix utf-8 on catalog
code = code.replace(/html = urllib\.request\.urlopen\(req\)\.read\(\)/g, "html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')");

// Fix utf-8 on details
code = code.replace(/html_detail = urllib\.request\.urlopen\(req_detail, timeout=10\)\.read\(\)/g, "html_detail = urllib.request.urlopen(req_detail, timeout=10).read().decode('utf-8', errors='ignore')");

// Fix actual_stock logic
code = code.replace(/actual_stock = -1[\s\S]*?actual_stock = int\(parts\[-1\]\)[\s\S]*?pass/g, 'actual_stock = -1');

// Fix dimensions extraction
const newDescCode = `if desc_text:
                    p['desc'] = desc_text
                    if 'alfombra' in p['name'].lower() or 'manta' in p['name'].lower():
                        import re
                        m1 = re.search(r'Medida.*?(\\d+.*?x.*?\\d+.*?cm)', desc_text, re.IGNORECASE)
                        m2 = re.search(r'(\\d+.*?x.*?\\d+.*?cm)', desc_text, re.IGNORECASE)
                        size = None
                        if m1: size = m1.group(1)
                        elif m2: size = m2.group(1)
                        if size:
                            if not p['name'].endswith(size.strip()):
                                p['name'] = f"{p['name']} - {size.strip()}"`;
code = code.replace(/if desc_text:\s+p\['desc'\] = desc_text/, newDescCode);

// Fix corrupted characters
code = code.replace(/pao/g, 'paño');
code = code.replace(/Paos/g, 'Paños');
code = code.replace(/\"bano\"/g, '\"baño\"');
code = code.replace(/Aade/g, 'Añade');
code = code.replace(/Diseado/g, 'Diseñado');
code = code.replace(/decoracin/g, 'decoración');
code = code.replace(/Bao/g, 'Baño');
code = code.replace(/Algodn/g, 'Algodón');

// Remove weird characters in "Agregar al carrito"
code = code.replace(/Agregar al carrito.*?'/g, "Agregar al carrito'");

fs.writeFileSync('build_catalog.py', code, 'utf8');
console.log('Fixed build_catalog.py!');
