"""
Scraper Playwright para tiendas A-G. Navega desde la página principal y extrae productos de cada tienda, guardando los CSV en data/raw/.
En cada ejecución descarga solo 5 tiendas nuevas (batch incremental).
"""
import os
import polars as pl
import logging
from playwright.sync_api import sync_playwright

RAW_DIR = os.path.join(os.path.dirname(__file__), "../data/raw")
SCRAPE_STATE_FILE = os.path.join(RAW_DIR, "scrape_state.txt")
BASE_URL = "https://starlit-toffee-5f30fa.netlify.app/"
TIENDAS = [
    ("tiendaA.csv", "Tienda A"),
    ("tiendaB.csv", "Tienda B"),
    ("tiendaC.csv", "Tienda C"),
    ("tiendaD.csv", "Tienda D"),
    ("tiendaE.csv", "Tienda E"),
    ("tiendaF.csv", "Tienda F"),
    ("tiendaG.csv", "Tienda G"),
]
COLUMNS = ["producto", "marca", "precio", "descripcion"]

def get_scrape_state():
    if not os.path.exists(SCRAPE_STATE_FILE):
        return 0
    with open(SCRAPE_STATE_FILE, "r", encoding="utf-8") as f:
        idx = f.read().strip()
        return int(idx) if idx.isdigit() else 0

def update_scrape_state(idx):
    with open(SCRAPE_STATE_FILE, "w", encoding="utf-8") as f:
        f.write(str(idx))

def scrape_tienda(page, tienda_nombre):
    import logging
    from bs4 import BeautifulSoup
    selector = f'a:text("{tienda_nombre}")'
    page.wait_for_selector(selector)
    page.click(selector)
    page.wait_for_timeout(2000)  # wait for products to load
    html = page.content()
    soup = BeautifulSoup(html, "html.parser")
    productos = []
    try:
        # Tienda B
        if tienda_nombre == "Tienda B":
            cards = soup.select('div.bg-white.rounded-2xl.overflow-hidden.shadow-xl.border-2.border-green-500.h-full')
            for card in cards:
                try:
                    producto = card.select_one('div.p-4.bg-green-500.text-white > h3').get_text(strip=True)
                    marca = card.select_one('div.p-4.bg-green-500.text-white > p').get_text(strip=True)
                    descripcion = card.select_one('div.p-4 > div.text-gray-700.text-sm > p').get_text(strip=True)
                    precio_raw = card.select_one('div.font-bold.text-xl.text-green-600').get_text(strip=True)
                    precio = precio_raw.replace('$', '').replace(',', '.').strip()
                    try:
                        precio_float = float(precio)
                    except Exception:
                        precio_float = None
                    productos.append({
                        "producto": producto,
                        "marca": marca,
                        "precio": precio_float,
                        "descripcion": descripcion
                    })
                except Exception as e:
                    logging.warning(f"No se pudo extraer un producto: {e}")

        # Tienda C
        elif tienda_nombre == "Tienda C":
            cards = soup.select('div.bg-gradient-to-br.from-red-50.to-white.rounded-xl.overflow-hidden.shadow-md.h-full.flex.flex-col.relative')
            for card in cards:
                try:
                    producto = card.select_one('div.p-5.flex.flex-col.flex-grow h3').get_text(strip=True)
                    marca = card.select_one('div.p-5.flex.flex-col.flex-grow .text-red-600').get_text(strip=True)
                    descripcion = card.select_one('div.p-5.flex.flex-col.flex-grow p.text-gray-600.text-sm.mb-4').get_text(strip=True)
                    precio_raw = card.select_one('div.absolute.top-0.right-0.bg-red-600.text-white.py-1.px-3.z-10.rounded-bl-lg.font-bold.text-sm').get_text(strip=True)
                    precio = precio_raw.replace('$', '').replace(',', '.').strip()
                    try:
                        precio_float = float(precio)
                    except Exception:
                        precio_float = None
                    productos.append({
                        "producto": producto,
                        "marca": marca,
                        "precio": precio_float,
                        "descripcion": descripcion
                    })
                except Exception as e:
                    logging.warning(f"No se pudo extraer un producto: {e}")

        # Tienda D
        elif tienda_nombre == "Tienda D":
            cards = soup.select('div.rounded-lg.overflow-hidden.h-full.flex.flex-col.bg-white')
            for card in cards:
                try:
                    producto = card.select_one('div.p-4.w-full > h3').get_text(strip=True)
                    marca = card.select_one('div.p-4.w-full > div.flex.justify-between.items-center > p.text-white\\/80.text-sm').get_text(strip=True)
                    descripcion = card.select_one('div.p-4.bg-purple-50.flex-grow > p').get_text(strip=True)
                    precio_raw = card.select_one('div.p-4.w-full > div.flex.justify-between.items-center > p.text-white.font-bold.text-lg').get_text(strip=True)
                    precio = precio_raw.replace('$', '').replace(',', '.').strip()
                    try:
                        precio_float = float(precio)
                    except Exception:
                        precio_float = None
                    productos.append({
                        "producto": producto,
                        "marca": marca,
                        "precio": precio_float,
                        "descripcion": descripcion
                    })
                except Exception as e:
                    logging.warning(f"No se pudo extraer un producto: {e}")

        # Tienda E
        elif tienda_nombre == "Tienda E":
            cards = soup.select('div.group.bg-white.rounded-lg.overflow-hidden.shadow-lg.h-full.flex.flex-col.border-2.border-transparent')
            for card in cards:
                try:
                    producto = card.select_one('h3.text-lg.font-bold.text-gray-900.leading-tight').get_text(strip=True)
                    marca = card.select_one('span.text-yellow-500.font-medium.text-sm').get_text(strip=True)
                    descripcion = card.select_one('div.mt-2.text-gray-600.text-sm.flex-grow > p').get_text(strip=True)
                    precio_raw = card.select_one('div.text-xl.font-bold.text-yellow-500').get_text(strip=True)
                    precio = precio_raw.replace('$', '').replace(',', '.').strip()
                    try:
                        precio_float = float(precio)
                    except Exception:
                        precio_float = None
                    productos.append({
                        "producto": producto,
                        "marca": marca,
                        "precio": precio_float,
                        "descripcion": descripcion
                    })
                except Exception as e:
                    logging.warning(f"No se pudo extraer un producto: {e}")

        # Tienda F tiene una estructura distinta
        if tienda_nombre == "Tienda F":
            page.wait_for_selector('div.group.bg-white.shadow-md.h-full.flex.flex-col.overflow-hidden', timeout=15000)
            cards = page.query_selector_all('div.group.bg-white.shadow-md.h-full.flex.flex-col.overflow-hidden')
            for card in cards:
                try:
                    marca = card.query_selector('span.text-indigo-600.font-medium.text-sm').inner_text().strip()
                    producto = card.query_selector('h3.text-lg.font-bold.text-gray-900.leading-tight.mb-2').inner_text().strip()
                    descripcion = card.query_selector('p.text-gray-600.text-sm.flex-grow').inner_text().strip()
                    precio_raw = card.query_selector('div.text-xl.font-bold.text-indigo-600').inner_text().strip()
                    precio = precio_raw.replace('$', '').replace(',', '.').strip()
                    try:
                        precio_float = float(precio)
                    except Exception:
                        precio_float = None
                    productos.append({
                        "producto": producto,
                        "marca": marca,
                        "precio": precio_float,
                        "descripcion": descripcion
                    })
                except Exception as e:
                    logging.warning(f"No se pudo extraer un producto: {e}")
        else:
            # Default: Tienda A y otras (ajustar según tienda)
            page.wait_for_selector('div.bg-white.rounded-lg.overflow-hidden.shadow-md.h-full.flex.flex-col', timeout=15000)
            cards = page.query_selector_all('div.bg-white.rounded-lg.overflow-hidden.shadow-md.h-full.flex.flex-col')
            for card in cards:
                try:
                    producto = card.query_selector('h3.text-lg.font-bold').inner_text().strip()
                    marca = card.query_selector('p.text-blue-600').inner_text().strip()
                    descripcion = card.query_selector('p.text-gray-600').inner_text().strip()
                    precio_raw = card.query_selector('div.bg-blue-600.text-white').inner_text().strip()
                    precio = precio_raw.replace('$', '').replace(',', '.').strip()
                    try:
                        precio_float = float(precio)
                    except Exception:
                        precio_float = None
                    productos.append({
                        "producto": producto,
                        "marca": marca,
                        "precio": precio_float,
                        "descripcion": descripcion
                    })
                except Exception as e:
                    logging.warning(f"No se pudo extraer un producto: {e}")
    except Exception as e:
        html_path = f"debug_{tienda_nombre.replace(' ', '_').lower()}.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(page.content())
        logging.error(f"No se encontró la tarjeta de producto para {tienda_nombre}. HTML guardado en {html_path}. Error: {e}")
    page.go_back()
    return productos

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    start_idx = get_scrape_state()
    batch = TIENDAS[start_idx:start_idx+5]
    if not batch:
        logging.info("No quedan tiendas nuevas por scrapear.")
        return
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(BASE_URL)
        for i, (fname, tienda_nombre) in enumerate(batch, start=start_idx):
            logging.info(f"Scrapeando {tienda_nombre} -> {fname}")
            productos = scrape_tienda(page, tienda_nombre)
            if productos:
                df = pl.DataFrame(productos)
                out_path = os.path.join(RAW_DIR, fname)
                df.write_csv(out_path)
                logging.info(f"Guardado {len(df)} productos en {fname}")
            else:
                logging.warning(f"No se extrajeron productos de {tienda_nombre}")
            update_scrape_state(i+1)
        browser.close()
    logging.info("Scraping completado para este batch.")

if __name__ == "__main__":
    main()
