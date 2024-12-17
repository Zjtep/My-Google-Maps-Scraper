import sys
import os
from bs4 import BeautifulSoup
import undetected_chromedriver as uc

# Add the scraper directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(current_dir, '..')))

from scraper.parser import Parser  # Import Parser directly
from scraper.communicator import Communicator
from scraper.datasaver import DataSaver


# Add the parent directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(current_dir, '..')))

def test_single_url():
    # Test URL for a single business
    test_url = r"https://www.google.com/maps/place/POPEYES+LOUISIANA+CHICKEN/@43.6647973,-79.346555,15z/data=!3m1!5s0x89d4cb7ec8991b4d:0x801cdc8a4b5771ff!4m6!3m5!1s0x89d4cb4a407bd9a7:0xa06bdce7172ebb9c!8m2!3d43.6685852!4d-79.3390983!16s%2Fg%2F11fqtqw1hk?entry=ttu&g_ep=EgoyMDI0MTIxMS4wIKXMDSoASAFQAw%3D%3D"

    # Use undetected_chromedriver to initialize WebDriver
    options = uc.ChromeOptions()
    options.headless = True  # Run headless for testing
    driver = uc.Chrome(options=options)

    try:
        print(f"Testing URL: {test_url}")
        driver.get(test_url)

        # Initialize the Parser class
        parser = Parser(driver)

        # Call the parser directly to parse the current page
        parser.parse()
        
        # Print out the parsed results
        if parser.finalData:
            for result in parser.finalData:
                print("Parsed Result:")
                for key, value in result.items():
                    print(f"{key}: {value}")
        else:
            print("No data parsed.")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_single_url()
