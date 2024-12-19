from bs4 import BeautifulSoup
from selenium import webdriver
from .error_codes import ERROR_CODES
from .communicator import Communicator
from .datasaver import DataSaver
from .base import Base
from .common import Common
from .email_extractor import WebCrawler  # Import WebCrawler from the email_extractor module

class Parser(Base):
    def __init__(self, driver) -> None:
        self.driver = driver
        self.finalData = []
        self.comparing_tool_tips = {
            "location": "Copy address",
            "phone": "Copy phone number",
            "website": "Open website",
            "booking": "Open booking link",
        }

    def init_data_saver(self):
        self.data_saver = DataSaver()

    def parse(self):
        """Parse the HTML of the business details sheet to extract key information, including email, phone, and LGBTQ+ friendly."""
        infoSheet = self.driver.execute_script(
            """return document.querySelector("[role='main']")"""
        )
        try:
            # Initialize data points
            data = {
                "Category": None,
                "Name": None,
                "Phone": None,
                "Google Maps URL": None,
                "Website": None,
                "Business Status": None,
                "Address": None,
                "Total Reviews": None,
                "Booking Links": None,
                "Rating": None,
                "Hours": None,
                "Email": None,
                "LGBTQ+ Friendly": None,
            }

            html = infoSheet.get_attribute("outerHTML")
            soup = BeautifulSoup(html, "html.parser")

            # Use selective parsing to reduce overhead
            try:
                data["Rating"] = soup.select_one("span.ceNzKf").get("aria-label", "").replace("stars", "").strip()
            except AttributeError:
                pass

            try:
                total_reviews_element = soup.select_one("div.F7nice")
                if total_reviews_element:
                    data["Total Reviews"] = total_reviews_element.get_text(strip=True)
            except AttributeError:
                pass

            try:
                data["Name"] = soup.select_one(".tAiQdd h1.DUwDvf").get_text(strip=True)
            except AttributeError:
                pass

            # Extract address, website, phone, and appointment link
            for infoBar in soup.select("button.CsEnBe"):
                data_tooltip = infoBar.get("data-tooltip", "")
                text = infoBar.select_one("div.rogA2c").get_text(strip=True) if infoBar.select_one("div.rogA2c") else ""

                if data_tooltip == self.comparing_tool_tips["location"]:
                    data["Address"] = text
                elif data_tooltip == self.comparing_tool_tips["phone"]:
                    data["Phone"] = text

            try:
                websiteTag = soup.select_one("a[aria-label*='Website']")
                if websiteTag:
                    data["Website"] = websiteTag.get("href")
            except AttributeError:
                pass

            try:
                bookingTag = soup.select_one("a[aria-label*='Open booking link']")
                if bookingTag:
                    data["Booking Links"] = bookingTag.get("href")
            except AttributeError:
                pass

            try:
                data["Hours"] = soup.select_one("div.t39EBf").get_text(strip=True)
            except AttributeError:
                pass

            try:
                data["Category"] = soup.select_one("button.DkEaL").get_text(strip=True)
            except AttributeError:
                pass

            data["Google Maps URL"] = self.driver.current_url

            try:
                businessStatus = soup.select_one("span.ZDu9vd span")
                if businessStatus:
                    data["Business Status"] = businessStatus.get_text(strip=True)
            except AttributeError:
                pass

            try:
                lgbtq_tag = soup.select_one("span:contains('LGBTQ+ friendly')")
                data["LGBTQ+ Friendly"] = "Yes" if lgbtq_tag else "No"
            except AttributeError:
                pass

            # Fallback: Use WebCrawler if phone or email is missing
            if not data["Phone"] or not data["Email"]:
                if data["Website"]:
                    print(f"Using WebCrawler to fetch missing data from: {data['Website']}")
                    web_crawler = WebCrawler(url=data["Website"])
                    if web_crawler.crawl():
                        data["Email"] = data["Email"] or web_crawler.get_email_from_website()
                        data["Phone"] = data["Phone"] or web_crawler.get_phone_from_website()

            self.finalData.append(data)

        except Exception as e:
            Communicator.show_error_message(
                f"Error occurred while parsing a location. Error is: {str(e)}",
                ERROR_CODES['ERR_WHILE_PARSING_DETAILS']
            )

    def main(self, allResultsLinks):
        Communicator.show_message("Scrolling is done. Now going to scrape each location")
        try:
            for resultLink in allResultsLinks:
                if Common.close_thread_is_set():
                    self.driver.quit()
                    return

                self.openingurl(url=resultLink)
                self.parse()

        except Exception as e:
            Communicator.show_message(f"Error occurred while parsing the locations. Error: {str(e)}")

        finally:
            self.init_data_saver()
            self.data_saver.save(datalist=self.finalData)
