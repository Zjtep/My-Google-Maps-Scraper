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
            # Updated regex for valid North American phone numbers
            phone_pattern = r"\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
            phone = re.findall(phone_pattern, html)
            nodup_phone = self.remove_dup_phone(phone)
            return [i.strip() for i in nodup_phone]
        except Exception as e:
            print(f"Phone search error: {e}")
            return []


    def fetch_page(self, url):
        """Fetch HTML content from a given URL."""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.content
            else:
                print(f"Unable to access {url} (Status code: {response.status_code})")
                return None
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def find_contact_page(self, html, base_url):
        """Search for links containing 'contact' and return the full URL."""
        soup = BeautifulSoup(html, "html.parser")
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if "contact" in href.lower():  # Check for 'contact' in the link
                if href.startswith("http"):  # Absolute URL
                    return href
                else:  # Relative URL
                    return f"{base_url.rstrip('/')}/{href.lstrip('/')}"
        return None

    def crawl(self):
        """Crawl the URL to fetch email and phone, including 'Contact Us' page."""
        if not self.url:
            print("No URL set for crawling.")
            return False

        base_url = self.url
        html = self.fetch_page(base_url)

        if not html:
            return False

        # Search for emails and phone numbers on the main page
        soup = BeautifulSoup(html, "html.parser")
        page_text = soup.get_text()
        emails = self.get_email(page_text)
        phones = self.get_phone(page_text)

        # Try finding a 'Contact Us' page
        contact_page_url = self.find_contact_page(html, base_url)
        if contact_page_url:
            print(f"Found 'Contact Us' page: {contact_page_url}")
            contact_html = self.fetch_page(contact_page_url)
            if contact_html:
                contact_text = BeautifulSoup(contact_html, "html.parser").get_text()
                emails.extend(self.get_email(contact_text))
                phones.extend(self.get_phone(contact_text))

        # Deduplicate and save the first found email and phone
        self.email = emails[0] if emails else "Not found"
        self.phone = phones[0] if phones else "Not found"

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
    crawler = WebCrawler(url="https://islamicsoccerleague.ca/")
    crawler.crawl()

    print("Final Results:")
    print("Email:", crawler.get_email_from_website())
    print("Phone:", crawler.get_phone_from_website())
