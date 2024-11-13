import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Initialize language mode
def get_all_links(url):
    links = set()
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    for link in soup.find_all('a', href=True):
        full_url = urljoin(url, link['href'])
        links.add(full_url)

    return links

def scrape_text_from_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text(separator=' ', strip=True)
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")
        return ""

def main():
    # URL of the webpage containing the list of websites
    list_page_url = "https://doj.gov.in"  # Replace with your target URL

    # Get all links from the list page
    all_links = get_all_links(list_page_url)

    # Scrape text from each link
    for link in all_links:
        print(f"Scraping {link}...")
        text = scrape_text_from_url(link)
        print(f"Text from {link}:\n{text}\n")

if __name__ == "__main__":
    main()
