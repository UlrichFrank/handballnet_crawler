import undetected_chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

# Initialize undetected Chrome
options = undetected_chrome.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-dev-shm-usage")
driver = undetected_chrome.Chrome(options=options)

try:
    BASE_URL = "https://www.handball.net"
    DATE_FROM = "2025-07-01"
    DATE_TO = "2026-06-30"
    LEAGUE_ID = "handball4all.baden-wuerttemberg.mc-ol-3-bw_bwhv"
    
    spielplan_url = f"{BASE_URL}/ligen/{LEAGUE_ID}/spielplan?dateFrom={DATE_FROM}&dateTo={DATE_TO}"
    
    print(f"Loading: {spielplan_url}")
    driver.get(spielplan_url)
    
    # Wait a bit for JavaScript to potentially run
    time.sleep(5)
    
    # Get page source
    page_source = driver.page_source
    
    # Check for various table-like elements
    print("\n=== Looking for table elements ===")
    tables = driver.find_elements(By.TAG_NAME, "table")
    print(f"Found {len(tables)} <table> elements")
    
    # Look for divs that might contain game data
    print("\n=== Looking for divs with game-like classes ===")
    divs = driver.find_elements(By.CSS_SELECTOR, "[class*='game'], [class*='spiel'], [class*='match']")
    print(f"Found {len(divs)} divs with game-like classes")
    
    # Look for specific containers
    print("\n=== Looking for common containers ===")
    containers = driver.find_elements(By.CSS_SELECTOR, ".container, .content, [role='main']")
    print(f"Found {len(containers)} container elements")
    
    # Print page title and heading
    print(f"\n=== Page Title ===")
    print(f"Title: {driver.title}")
    
    # Look for any h1 or h2
    headings = driver.find_elements(By.TAG_NAME, "h1")
    print(f"H1 headings: {[h.text for h in headings[:3]]}")
    
    # Check if we can find the game count (90)
    print(f"\n=== Looking for page numbers / game count ===")
    body_text = driver.find_element(By.TAG_NAME, "body").text
    if "90" in body_text:
        print("Found '90' in page text (game count visible)")
    
    # Look for pagination elements
    print(f"\n=== Looking for pagination ===")
    buttons = driver.find_elements(By.TAG_NAME, "button")
    print(f"Found {len(buttons)} buttons")
    for btn in buttons[:10]:
        print(f"  - {btn.get_attribute('class')}: {btn.text}")
    
    # Look specifically for "next" or ">" buttons
    next_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), '>')]")
    print(f"Found {len(next_buttons)} buttons with '>'")
    
    # Check for links that might be the game data
    print(f"\n=== Looking for game links ===")
    links = driver.find_elements(By.TAG_NAME, "a")
    game_links = [l for l in links if "aufstellung" in l.get_attribute("href").lower()]
    print(f"Found {len(game_links)} links with 'aufstellung'")
    if game_links:
        print(f"First game link: {game_links[0].get_attribute('href')}")
    
    # Check for any visible text in main content area
    print(f"\n=== Sampling visible text ===")
    text_content = driver.find_element(By.TAG_NAME, "body").text
    lines = [l.strip() for l in text_content.split('\n') if l.strip()]
    print(f"Total text lines: {len(lines)}")
    print("First 20 lines:")
    for line in lines[:20]:
        print(f"  {line}")
    
finally:
    driver.quit()
