"""
scrape_and_save.py

Scrapes a list of URLs (tries requests+BS4 first; falls back to Selenium if page appears JS-rendered)
and saves visible text into individual UTF-8 .txt files in the `scraped_data/` folder.

Usage:
    python scrape_and_save.py
"""

from urllib.parse import urlparse, urljoin
import os, re, time
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter, Retry

# Selenium imports (used only when needed)
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# -----------------------
# Configure / Edit URLs
# -----------------------
loan_links = [
    "https://bankofmaharashtra.bank.in/credit-facilities-to-entrepreneurs",
    "https://bankofmaharashtra.bank.in/educational-loans",
    "https://bankofmaharashtra.bank.in/loan-for-covid-affected-tourism-service",
    "https://bankofmaharashtra.bank.in/mahabank-professional-loan-scheme-mpls",
    "https://bankofmaharashtra.bank.in/maha-adhaar-loan",
    "https://bankofmaharashtra.bank.in/maha-super-flexi-housing-loan-scheme",
    "https://digileads.bankofmaharashtra.in/carloan?bom",
    "https://bankofmaharashtra.bank.in/loan-against-property",
    "https://bankofmaharashtra.bank.in/msme-machinery-equipment-scheme",
    "https://bankofmaharashtra.bank.in/mahabank-vehicle-loan-scheme-for-second-hand-car",
    "https://bankofmaharashtra.bank.in/msme-gold-loan",
    "https://bomdigitalloans.bankofmaharashtra.bank.in/gold-loan/#/gold-loan-signin?pri=bom",
    "https://bankofmaharashtra.bank.in/agri-gold-loan",
    "https://bankofmaharashtra.bank.in/scheme-for-subordinate-debt",
    "https://bankofmaharashtra.bank.in/maha-lap-mortgage-loan",
    "https://bankofmaharashtra.bank.in/collateral-free-cash-credit-facility",
    "https://bankofmaharashtra.bank.in/working-capital",
    "https://bankofmaharashtra.bank.in/personal-banking/loans/personal-loan",
    "https://digileads.bankofmaharashtra.in/educationloan?bom",
    "https://digileads.bankofmaharashtra.in/homeloan?bom",
    "https://digiloans.bankofmaharashtra.bank.in/apply/vehicleloan?bom",
    "https://bankofmaharashtra.bank.in/kisan-credit-card",
    "https://bankofmaharashtra.bank.in/topup-home-loan",
    "https://bankofmaharashtra.bank.in/hotel-and-restaurant-loan",
    "https://bankofmaharashtra.bank.in/loan-against-warehouse-receipts-to-farmers",
    "https://bankofmaharashtra.bank.in/mahabank-loan-scheme-for-doctors",
    "https://bankofmaharashtra.bank.in/guaranteed-emergency-credit-line",
    "https://bankofmaharashtra.bank.in/collateral-free-term-loan-facility",
    "https://bankofmaharashtra.bank.in/gold-loan",
    "https://bankofmaharashtra.bank.in/personal-banking/loans/home-loan",
    "https://bankofmaharashtra.bank.in/ms-loan-tap-credit-products",
    "https://bankofmaharashtra.bank.in/vehicle-loan-for-small-road-transport-operator",
    "https://bankofmaharashtra.bank.in/personal-banking/loans/car-loan",
    "https://bankofmaharashtra.bank.in/personal-banking/loans/car-loan#crLmsme",
    "https://bankofmaharashtra.bank.in/personal-banking/loans/car-loan#msmeCols",
    "https://bankofmaharashtra.bank.in/personal-banking/loans/car-loan#pane-elig",
    "https://bankofmaharashtra.bank.in/personal-banking/loans/car-loan#msmegovs",
    "https://bankofmaharashtra.bank.in/personal-banking/loans/car-loan#pane-fb",
    "https://bankofmaharashtra.bank.in/personal-banking/loans/car-loan#crBs",
    "https://bankofmaharashtra.bank.in/personal-banking/loans/car-loan#pbTermDeposit",
    "https://bankofmaharashtra.bank.in/personal-banking/loans/car-loan#pane-ir",
    "https://bankofmaharashtra.bank.in/personal-banking/loans/car-loan#agLoans",
    "https://bankofmaharashtra.bank.in/personal-banking/loans/car-loan#0",
    "https://bankofmaharashtra.bank.in/personal-banking/loans/car-loan#msmeZEDs",
    "https://bankofmaharashtra.bank.in/personal-banking/loans/car-loan#msmeSL",
    "https://bankofmaharashtra.bank.in/personal-banking/loans/car-loan#pane-hta",
    "https://bankofmaharashtra.bank.in/personal-banking/loans/car-loan#pane-emi",
    "https://bankofmaharashtra.bank.in/personal-banking/loans/car-loan#msmeOGSs",
    "https://bankofmaharashtra.bank.in/personal-banking/loans/car-loan#msmeMSSs",
    "https://bankofmaharashtra.bank.in/personal-banking/loans/car-loan#nriProducts",
]

# -----------------------
# Output folder & helper
# -----------------------
output_folder = "scraped_data"
os.makedirs(output_folder, exist_ok=True)

def clean_filename(url):
    parsed = urlparse(url)
    # combine host + path + query fragment to avoid name collisions
    parts = (parsed.netloc + parsed.path + ("_" + parsed.fragment if parsed.fragment else "")).strip()
    name = re.sub(r"[^\w\-._]", "_", parts)  # safe
    name = name.strip("_")
    if not name:
        name = "page"
    return name + ".txt"

# -----------------------
# Requests session with retries
# -----------------------
def make_requests_session(retries=3, backoff=0.3):
    session = requests.Session()
    retries_policy = Retry(total=retries, backoff_factor=backoff, status_forcelist=[429,500,502,503,504])
    session.mount("https://", HTTPAdapter(max_retries=retries_policy))
    session.mount("http://", HTTPAdapter(max_retries=retries_policy))
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"
    })
    return session

# -----------------------
# Extract visible text from soup
# -----------------------
def get_visible_text_from_html(html):
    soup = BeautifulSoup(html, "lxml")
    # remove script/style
    for tag in soup(["script", "style", "noscript", "header", "footer", "svg"]):
        tag.decompose()
    texts = []
    for el in soup.find_all(text=True):
        text = el.strip()
        if text:
            texts.append(text)
    visible = "\n".join(texts)
    # reduce excessive whitespace
    visible = re.sub(r"\n\s+\n", "\n\n", visible)
    return visible

# -----------------------
# Selenium fallback
# -----------------------
def fetch_with_selenium(url, wait_seconds=2, scroll_pause=1.0, max_scrolls=10):
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-gpu")
    # avoid logging spam
    opts.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)
    try:
        driver.set_page_load_timeout(30)
        driver.get(url)
        time.sleep(wait_seconds)
        last_height = driver.execute_script("return document.body.scrollHeight")
        scrolls = 0
        while scrolls < max_scrolls:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            scrolls += 1
        html = driver.page_source
        text = get_visible_text_from_html(html)
        return text, html
    except Exception as e:
        print("Selenium error for", url, "->", e)
        return "", ""
    finally:
        driver.quit()

# -----------------------
# Main scrape loop
# -----------------------
def scrape_and_save(urls):
    session = make_requests_session()
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Processing: {url}")
        filename = clean_filename(url)
        out_path = os.path.join(output_folder, filename)

        try:
            resp = session.get(url, timeout=20)
            html = resp.text if resp.status_code == 200 else ""
        except Exception as e:
            print("Requests error:", e)
            html = ""

        text = ""
        if html:
            text = get_visible_text_from_html(html)

        # Heuristic: if visible text is too short, use Selenium fallback
        if len(text) < 200:
            print("-> Detected little content from requests; falling back to Selenium...")
            text, html = fetch_with_selenium(url)

        # Save text
        if not text:
            print("-> No text extracted for:", url)
            text = f"[No text extracted]\nURL: {url}\n"

        with open(out_path, "w", encoding="utf-8", errors="ignore") as f:
            f.write(f"Source: {url}\n\n")
            f.write(text)

        print("Saved:", out_path)

        # polite delay between requests
        time.sleep(1.0)

    print("\nAll done. Files saved to:", os.path.abspath(output_folder))

if __name__ == "__main__":
    scrape_and_save(loan_links)
