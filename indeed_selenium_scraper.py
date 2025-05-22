from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import yaml
import pandas as pd
import time

def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

def build_query(keyword, location):
    return f"https://www.indeed.com/jobs?q={keyword}&l={location}"

def scrape_with_selenium(keyword, location, max_results=10):
    options = Options()
    # 🟡 Headless mode is OFF so you can see what happens
    # options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    url = build_query(keyword, location)
    print(f"🔍 Loading: {url}")
    driver.get(url)
    time.sleep(4)  # wait for page to load

    jobs = []
    job_cards = driver.find_elements(By.CLASS_NAME, 'job_seen_beacon')

    for card in job_cards[:max_results]:
        try:
            title = card.find_element(By.TAG_NAME, 'h2').text
            company = card.find_element(By.CLASS_NAME, 'companyName').text
            location = card.find_element(By.CLASS_NAME, 'companyLocation').text
            link = card.find_element(By.TAG_NAME, 'a').get_attribute('href')
            snippet = card.find_element(By.CLASS_NAME, 'job-snippet').text
            jobs.append({
                "title": title,
                "company": company,
                "location": location,
                "link": link,
                "summary": snippet.strip().replace('\n', ' ')
            })
        except Exception:
            continue

    driver.quit()
    return jobs

def save_results(jobs, filename="indeed_jobs.csv"):
    df = pd.DataFrame(jobs).drop_duplicates(subset=["link"])
    df.to_csv(filename, index=False)
    print(f"✅ Saved {len(df)} unique jobs to {filename}")

if __name__ == "__main__":
    config = load_config()
    all_jobs = []

    for keyword in config['job_title_keywords']:
        print(f"\n🔎 Searching for: {keyword}")
        jobs = scrape_with_selenium(keyword, config['location_preference']['base_city'])
        all_jobs.extend(jobs)
        time.sleep(2)

    save_results(all_jobs)
