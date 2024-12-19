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
    #test_url = r"https://www.google.com/maps/place/Bazooka+Kickboxing+%26+MMA/@43.7774064,-79.2513025,17z/data=!3m1!4b1!4m6!3m5!1s0x89d4d1aa42954655:0x1437226f9279d76c!8m2!3d43.7774026!4d-79.2487276!16s%2Fg%2F11bymwt61v?entry=ttu&g_ep=EgoyMDI0MTIxMS4wIKXMDSoASAFQAw%3D%3D"

    test_url = r"https://www.google.com/maps/place/UKB+-+Ultimate+Kickboxing+for+Women/data=!4m7!3m6!1s0x882b3f02ea1fec0f:0xb1bdfd357f139dcc!8m2!3d43.6664714!4d-79.6846666!16s%2Fg%2F11b5wnnbz3!19sChIJD-wf6gI_K4gRzJ0TfzX9vbE?authuser=0&hl=en&rclk=1"

    # Use undetected_chromedriver to initialize WebDriver
    options = uc.ChromeOptions()
    options.headless = False  # Run headless for testing
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
