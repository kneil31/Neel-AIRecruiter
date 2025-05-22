import requests
from bs4 import BeautifulSoup
import yaml
import pandas as pd
import urllib.parse
import time

def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

def build_query(keyword, location):
    keyword_encoded = urllib.parse.quote_plus(keyword)
    location_encoded = urllib.parse.quote(location)
    return f"https://www.indeed.com/jobs?q={keyword_encoded}&l={location_encoded}&radius=25"

def scrape_indeed(url, max_results=10):
    results = []
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # ✅ Updated class for job listings
    cards = soup.find_all('a', class_='css-ujz8p5', limit=max_results)

    for card in cards:
        try:
            title = card.find('h2').text.strip()
            company = card.find('span', class_='companyName').text.strip()
            location = card.find('div', class_='companyLocation').text.strip()
            link = "https://www.indeed.com" + card.get('href')
            snippet = card.find('div', class_='job-snippet').text.strip().replace('\n', ' ')
            results.append({
                "title": title,
                "company": company,
                "location": location,
                "link": link,
                "summary": snippet
            })
        except Exception as e:
            continue
    return results

def save_results(jobs, filename="indeed_jobs.csv"):
    df = pd.DataFrame(jobs).drop_duplicates(subset=["link"])
    df.to_csv(filename, index=False)
    print(f"Saved {len(df)} unique jobs to {filename}")

if __name__ == "__main__":
    config = load_config()
    all_jobs = []

    for keyword in config['job_title_keywords']:
        url = build_query(keyword, config['location_preference']['base_city'])
        print(f"Searching: {url}")
        jobs = scrape_indeed(url)
        all_jobs.extend(jobs)
        time.sleep(1)  # Sleep to avoid rate limits

    save_results(all_jobs)
