from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from playwright.async_api import async_playwright
import re, asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok", "message": "Oba.az qiymət API"}

@app.get("/search")
async def search(q: str):
    if not q or len(q.strip()) < 1:
        raise HTTPException(400, "Axtarış sözü lazımdır")
    
    results = await scrape_oba(q.strip())
    return {
        "query": q,
        "results": results,
        "count": len(results)
    }

async def scrape_oba(query: str):
    url = f"https://oba.az/search?q={query}"
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(2000)

            # Məhsul kartlarını tap
            items = await page.query_selector_all('[class*="ProductCard"], [class*="product-card"], [class*="ProductItem"], .product')
            
            for item in items[:8]:
                try:
                    name_el = await item.query_selector('[class*="name"], [class*="title"], [class*="Name"], h3, h4')
                    price_el = await item.query_selector('[class*="price"], [class*="Price"]')
                    img_el = await item.query_selector('img')
                    link_el = await item.query_selector('a')

                    name = await name_el.inner_text() if name_el else ""
                    price_raw = await price_el.inner_text() if price_el else ""
                    img = await img_el.get_attribute("src") if img_el else ""
                    href = await link_el.get_attribute("href") if link_el else ""

                    price_match = re.search(r'[\d.,]+', price_raw)
                    price = price_match.group() if price_match else ""

                    if name.strip() and price:
                        results.append({
                            "name": name.strip()[:80],
                            "price": price,
                            "image": img or "",
                            "url": f"https://oba.az{href}" if href and href.startswith("/") else href or ""
                        })
                except:
                    continue

            # Əgər kartlar tapılmadısa JSON API-dən cəhd et
            if not results:
                try:
                    response = await page.evaluate("""async (q) => {
                        const r = await fetch('/api/products/search?q=' + encodeURIComponent(q) + '&per_page=8');
                        if (r.ok) return await r.json();
                        return null;
                    }""", query)
                    
                    if response:
                        items_data = (response.get("data") or 
                                     response.get("products") or 
                                     response.get("items") or [])
                        for p in items_data[:8]:
                            name = p.get("name") or p.get("title") or ""
                            price = str(p.get("price") or p.get("current_price") or "")
                            if name and price:
                                results.append({
                                    "name": str(name)[:80],
                                    "price": price,
                                    "image": p.get("image") or p.get("photo") or "",
                                    "url": p.get("url") or p.get("link") or ""
                                })
                except:
                    pass

        except Exception as e:
            print(f"Scrape xətası: {e}")
        finally:
            await browser.close()

    return results
