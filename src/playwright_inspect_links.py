"""
Script Playwright para listar todos los enlaces y textos clicables en la página principal del portal de tiendas.
"""
from playwright.sync_api import sync_playwright

BASE_URL = "https://starlit-toffee-5f30fa.netlify.app/"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(BASE_URL)
        print("--- ENLACES <a> ---")
        for a in page.query_selector_all("a"):
            print(f"href={a.get_attribute('href')}, text={a.inner_text().strip()}")
        print("\n--- BOTONES <button> ---")
        for b in page.query_selector_all("button"):
            print(f"text={b.inner_text().strip()}")
        print("\n--- DIVS CLICABLES ---")
        for d in page.query_selector_all("div"):
            onclick = d.get_attribute('onclick')
            if onclick or 'click' in d.get_attribute('class') or 'card' in (d.get_attribute('class') or ''):
                print(f"class={d.get_attribute('class')}, text={d.inner_text().strip()}")
        browser.close()

if __name__ == "__main__":
    main()
