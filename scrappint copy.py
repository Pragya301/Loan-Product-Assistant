url_list = [
    "https://bankofmaharashtra.in/personal-banking/loans/home-loan",
    "https://bankofmaharashtra.in/personal-banking/loans/car-loan",
    "https://bankofmaharashtra.in/personal-banking/loans/personal-loan"
]
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin
import time
from webdriver_manager.chrome import ChromeDriverManager

def scrape_page(url):
    print("\n========== SCRAPING ==========")
    print("URL:", url)
    print("================================\n")

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    driver.get(url)

    # Wait for at least some content
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
    except:
        pass

    # Scroll fully to load dynamic content
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # --- EXTRACT ALL TEXT ---
    elements = driver.find_elements(By.XPATH, "//*[not(self::script) and not(self::style)]")
    all_text = "\n".join([el.text.strip() for el in elements if el.text.strip()])

    print("=== TEXT EXTRACTED ===\n")
    print(all_text[:2000])  # print first 2000 chars (to avoid huge output)
    print("\n(Full text stored in variable: all_text)\n")

    # --- EXTRACT ALL LINKS (<a>) ---
    link_elements = driver.find_elements(By.TAG_NAME, "a")

    all_links = set()

    for item in link_elements:
        href = item.get_attribute("href")
        if href:
            full_url = urljoin(url, href)
            all_links.add(full_url)

    print(f"\n=== FOUND {len(all_links)} LINKS ===\n")

    for link in all_links:
        print(link)

    print("\n========== DONE ==========\n")
    driver.quit()

    return all_text, list(all_links)



# Run on Car Loan page
scrape_page("https://bankofmaharashtra.in/personal-banking/loans/car-loan")

