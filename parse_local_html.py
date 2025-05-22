import argparse
import json
from bs4 import BeautifulSoup
import pandas as pd


def parse_saved_html(html_path):
    """Parse a saved Indeed or LinkedIn search result HTML file."""
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    jobs = []

    # Attempt multiple selectors for robustness
    job_cards = soup.select("a[data-hide-spinner='true']")
    if not job_cards:
        job_cards = soup.select("a.tapItem")
    if not job_cards:
        job_cards = soup.find_all("a", class_="jobtitle")

    for card in job_cards:
        try:
            # Title can be in h2 or as aria-label/title attribute
            title_tag = card.find("h2")
            title = title_tag.get_text(strip=True) if title_tag else card.get("title", "").strip()

            company_tag = card.find(class_="companyName") or card.find("span", class_="company")
            company = company_tag.get_text(strip=True) if company_tag else ""

            location_tag = card.find(class_="companyLocation") or card.find("div", class_="location")
            location = location_tag.get_text(strip=True) if location_tag else ""

            snippet_tag = card.find("div", class_="job-snippet") or card.find("div", class_="summary")
            snippet = snippet_tag.get_text(strip=True).replace("\n", " ") if snippet_tag else ""

            link = card.get("href", "")
            if link and not link.startswith("http"):
                link = "https://www.indeed.com" + link

            jobs.append({
                "title": title,
                "company": company,
                "location": location,
                "link": link,
                "summary": snippet,
            })
        except Exception:
            continue

    return jobs


def save_to_csv(jobs, output_path):
    df = pd.DataFrame(jobs).drop_duplicates(subset=["link"])
    df.to_csv(output_path, index=False)
    print(f"Saved {len(df)} jobs to {output_path}")


def save_to_json(jobs, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(jobs)} jobs to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse a saved job search HTML page")
    parser.add_argument("html_path", help="Path to the saved HTML file")
    parser.add_argument("--csv", help="Path to output CSV file")
    parser.add_argument("--json", help="Path to output JSON file")
    args = parser.parse_args()

    extracted = parse_saved_html(args.html_path)

    if args.csv:
        save_to_csv(extracted, args.csv)
    if args.json:
        save_to_json(extracted, args.json)

    if not args.csv and not args.json:
        print(json.dumps(extracted, indent=2))

