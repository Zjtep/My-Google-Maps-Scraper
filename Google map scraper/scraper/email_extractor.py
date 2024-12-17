import coloredlogs
import logging
import requests
import re
from bs4 import BeautifulSoup

requests.packages.urllib3.disable_warnings()

FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

logging.basicConfig(level=logging.DEBUG, format=FORMAT)
logger = logging.getLogger(__name__)
coloredlogs.install(logger=logger)

class WebCrawler:
    def __init__(self, url=None):
        """Initialize the WebCrawler with an optional URL."""
        self.url = url
        self.email = ""
        self.phone = ""
        
    def set_url(self, url):
        """Set or update the URL for crawling."""
        self.url = url
        
    def remove_dup_email(self, x):
        """Remove duplicate emails."""
        return list(dict.fromkeys(x))

    def remove_dup_phone(self, x):
        """Remove duplicate phone numbers."""
        return list(dict.fromkeys(x))

    def get_email(self, html):
        """Extract email addresses from HTML content."""
        try:
            email = re.findall("[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,3}", html)
            nodup_email = self.remove_dup_email(email)
            return [i.strip() for i in nodup_email]
        except Exception as e:
            logger.error(f"Email search error: {e}")
            return []

    def get_phone(self, html):
        """Extract phone numbers from HTML content."""
        try:
            phone_pattern = r"(?:(?:8|\+7)[\- ]?)?(?:\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}"
            phone = re.findall(phone_pattern, html)
            nodup_phone = self.remove_dup_phone(phone)
            return [i.strip() for i in nodup_phone]
        except Exception as e:
            logger.error(f"Phone search error: {e}")
            return []

    def crawl(self):
        """Crawl the URL to fetch email and phone."""
        if not self.url:
            logger.error("No URL set for crawling.")
            return False
        
        try:
            # Send a GET request to the website
            response = requests.get(self.url, verify=False)
            
            # Check if the request was successful (status code 200)
            if response.status_code != 200:
                logger.warning(f"Unable to access {self.url} (Status code: {response.status_code})")
                return False
            
            # Parse the page content using BeautifulSoup
            soup = BeautifulSoup(response.content, 'lxml', from_encoding=response.encoding)
            
            # Get emails and phones from the page
            emails = self.get_email(soup.get_text())
            phones = self.get_phone(soup.get_text())
            
            # Set the first found email and phone, or empty string if none found
            self.email = emails[0] if emails else ""
            self.phone = phones[0] if phones else ""
            
            logger.info(f"Found email: {self.email}")
            logger.info(f"Found phone: {self.phone}")
            return True
        
        except Exception as e:
            logger.error(f"Error occurred while crawling {self.url}: {e}")
            return False

    def get_email_from_website(self):
        """Return the email from the crawled URL."""
        return self.email

    def get_phone_from_website(self):
        """Return the phone number from the crawled URL."""
        return self.phone

    def print_results(self):
        """Print the results."""
        print(f"Email: {self.email}")
        print(f"Phone: {self.phone}")


if __name__ == "__main__":
    # Example usage:
    # Initialize with a URL
    crawler = WebCrawler(url="https://www.theacademytoronto.ca/")
    
    # Crawl to fetch email and phone
    crawler.crawl()
    
    # Get and print the email and phone
    crawler.print_results()
    
    # If you need to set a new URL and fetch new data:
    crawler.set_url("https://www.bazookakickboxing.ca/")
    crawler.crawl()
    crawler.get_phone_from_website()
