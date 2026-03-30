import requests
from bs4 import BeautifulSoup
import re

JACOB_URL = "https://www.cs.tufts.edu/~jacob/papers/"
LAB_FILE = "publications.html"

def normalize(text):
    """Normalize text for duplicate detection."""
    return re.sub(r"\s+", " ", text).strip().lower()

def extract_year(text):
    """Extract a 4-digit year from a publication entry."""
    match = re.search(r"\b(20\d{2}|19\d{2})\b", text)
    return match.group(1) if match else None

def scrape_jacob():
    """Scrape publications from Jacob's page."""
    html = requests.get(JACOB_URL).text
    soup = BeautifulSoup(html, "html.parser")

    pubs = []
    for p in soup.find_all("p"):
        text = p.get_text(" ", strip=True)
        if not text or len(text) < 20:
            continue

        year = extract_year(text)
        if not year:
            continue

        # PDF link if present
        pdf = None
        link = p.find("a", href=True)
        if link and link["href"].lower().endswith(".pdf"):
            href = link["href"]
            pdf = href if href.startswith("http") else JACOB_URL + href

        pubs.append({
            "year": year,
            "raw": text,
            "norm": normalize(text),
            "pdf": pdf
        })

    return pubs

def load_lab_page():
    """Load and parse the lab's publications.html."""
    with open(LAB_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")

    # Build a set of existing normalized entries
    existing = set()
    for li in soup.find_all("li"):
        existing.add(normalize(li.get_text(" ", strip=True)))

    return soup, existing

def find_or_create_year_section(soup, year):
    """Find the <ul> under <h4>YEAR</h4>, or create it if missing."""
    # Look for <h4>YEAR</h4>
    h4 = soup.find("h4", string=year)
    if h4:
        # The next <ul> after this <h4>
        ul = h4.find_next_sibling("ul")
        if ul:
            return ul

    # If not found, create a new section at the top of the page
    main_section = soup.find("section", id="main")

    new_h4 = soup.new_tag("h4")
    new_h4.string = year

    new_ul = soup.new_tag("ul")

    # Insert at the top (after the header)
    header = main_section.find("header")
    header.insert_after(new_ul)
    new_ul.insert_before(new_h4)

    return new_ul

def format_li(pub):
    """Format a publication as an <li>."""
    if pub["pdf"]:
        return f'<li><a href="{pub["pdf"]}">{pub["raw"]}</a></li>'
    return f"<li>{pub['raw']}</li>"

def main():
    jacob_pubs = scrape_jacob()
    soup, existing = load_lab_page()

    new_count = 0

    for pub in jacob_pubs:
        if pub["norm"] in existing:
            continue  # skip duplicates

        year = pub["year"]
        ul = find_or_create_year_section(soup, year)

        li_html = format_li(pub)
        ul.append(BeautifulSoup(li_html, "html.parser"))

        new_count += 1

    with open(LAB_FILE, "w", encoding="utf-8") as f:
        f.write(str(soup))

    print(f"Added {new_count} new publications.")

if __name__ == "__main__":
    main()
