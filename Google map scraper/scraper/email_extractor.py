import requests
import re
from bs4 import BeautifulSoup

class WebCrawler:
    def __init__(self, url=None):
        self.url = url
        self.email = ""
        self.phone = ""

    def set_url(self, url):
        """Set or update the URL for crawling."""
        self.url = url

    def remove_dup(self, data):
        """Remove duplicate entries."""
        return list(dict.fromkeys(data))

    def get_email(self, html):
        """Extract email addresses from HTML content."""
        email_pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
        return self.remove_dup(re.findall(email_pattern, html))

    def get_phone(self, html):
        """Extract valid phone numbers from HTML content."""
        try:
            phone_pattern = r"\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
            phone = re.findall(phone_pattern, html)
            return self.remove_dup([p.strip() for p in phone])
        except Exception as e:
            print(f"Phone search error: {e}")
            return []

    def fetch_page(self, url):
        """Fetch HTML content from a given URL."""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Connection": "keep-alive",
            }
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.content
            else:
                print(f"Unable to access {url} (Status code: {response.status_code})")
                return None
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def find_targeted_pages(self, html, base_url):
        """Search for internal links likely to contain contact information."""
        soup = BeautifulSoup(html, "html.parser")
        keywords = ["contact", "about", "locations", "reach", "info"]  # Keywords for filtering
        targeted_pages = []
        for link in soup.find_all("a", href=True):
            href = link["href"].lower()
            if any(keyword in href for keyword in keywords):
                if href.startswith("http"):  # Absolute URL
                    targeted_pages.append(href)
                else:  # Relative URL
                    targeted_pages.append(f"{base_url.rstrip('/')}/{href.lstrip('/')}")
        return self.remove_dup(targeted_pages)

    def crawl(self):
        """Crawl the URL to fetch email and phone, including targeted pages."""
        if not self.url:
            print("No URL set for crawling.")
            return False

        html = self.fetch_page(self.url)

        if not html:
            return False

        # Parse the homepage content
        soup = BeautifulSoup(html, "html.parser")
        page_text = soup.get_text(separator="\n")  # Extract all text with newlines
        print(f"Extracted Page Text:\n{page_text}")  # Debug output to verify content

        # Extract emails and phones from homepage text
        emails = self.get_email(page_text)
        phones = self.get_phone(page_text)

        if emails:
            self.email = emails[0]
        if phones:
            self.phone = phones[0]

        if self.email and self.phone:  # Stop crawling if both are found on the homepage
            print("Email and phone found on the homepage. Stopping further crawling.")
            return True

        # Find and crawl targeted pages
        targeted_pages = self.find_targeted_pages(html, self.url)
        for page in targeted_pages:
            print(f"Searching targeted page: {page}")
            page_html = self.fetch_page(page)
            if page_html:
                page_text = BeautifulSoup(page_html, "html.parser").get_text(separator="\n")
                print(f"Extracted Page Text from {page}:\n{page_text}")  # Debug output for each page

                if not self.email:
                    emails = self.get_email(page_text)
                    if emails:
                        self.email = emails[0]

                if not self.phone:
                    phones = self.get_phone(page_text)
                    if phones:
                        self.phone = phones[0]

                if self.email and self.phone:  # Stop if both email and phone are found
                    print("Email and phone found. Stopping further crawling.")
                    break

        print(f"Found email: {self.email}")
        print(f"Found phone: {self.phone}")
        return True

    def get_email_from_website(self):
        """Return the email from the crawled URL."""
        return self.email

    def get_phone_from_website(self):
        """Return the phone number from the crawled URL."""
        return self.phone


if __name__ == "__main__":
    # Example usage:
    crawler = WebCrawler(url="http://submissionsbjjacademy.com/")
    crawler.crawl()

    print("Final Results:")
    print("Email:", crawler.get_email_from_website())
    print("Phone:", crawler.get_phone_from_website())
