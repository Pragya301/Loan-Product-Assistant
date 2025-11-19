from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urljoin
import time

def scrape_page(url):
    print("\n========== SCRAPING ==========")
    print("URL:", url)
    print("================================\n")

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    driver.get(url)

    # Wait for content
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
    except:
        pass

    # Scroll
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Extract text
    elements = driver.find_elements(By.XPATH, "//body//*[not(self::script)][not(self::style)]")
    all_text = "\n".join([el.text.strip() for el in elements if el.text.strip()])

    print("=== TEXT EXTRACTED ===\n")
    print(all_text[:2000].encode("utf-8", "ignore").decode())

    # Extract links
    link_elements = driver.find_elements(By.TAG_NAME, "a")
    all_links = {
        urljoin(url, item.get_attribute("href"))
        for item in link_elements
        if item.get_attribute("href")
    }

    print(f"\n=== FOUND {len(all_links)} LINKS ===\n")
    for link in all_links:
        print(link)

    print("\n========== DONE ==========\n")
    driver.quit()

    return all_text, list(all_links)

# Run properly
scrape_page("https://bankofmaharashtra.in/personal-banking/loans/car-loan")
