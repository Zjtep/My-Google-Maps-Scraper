import coloredlogs
import logging
from threading import Thread
from queue import Queue
import requests
import re
import pandas as pd
from bs4 import BeautifulSoup
import requests_random_user_agent

requests.packages.urllib3.disable_warnings()

FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

logging.basicConfig(level=logging.DEBUG, format=FORMAT)
logger = logging.getLogger(__name__)
coloredlogs.install(logger=logger)

class EmailPhoneExtractor:
    @staticmethod
    def remove_dup_email(emails):
        return list(dict.fromkeys(emails))

    @staticmethod
    def remove_dup_phone(phones):
        return list(dict.fromkeys(phones))

    @staticmethod
    def get_email(html):
        try:
            email = re.findall("[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,3}", html)
            return [i.strip() for i in EmailPhoneExtractor.remove_dup_email(email)]
        except Exception as e:
            logger.error(f"Email search error: {e}")
            return []

    @staticmethod
    def get_phone(html):
        try:
            phone_pattern = r"(?:(?:8|\+7)[\- ]?)?(?:\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}"
            phone = re.findall(phone_pattern, html)
            return [i.strip() for i in EmailPhoneExtractor.remove_dup_phone(phone)]
        except Exception as e:
            logger.error(f"Phone search error: {e}")
            return []

class URLReader:
    @staticmethod
    def read_file(file_path='web_urls.txt'):
        urls = []
        with open(file_path, 'r') as f:
            for line in f.readlines():
                url = line.strip()
                if not url.startswith('http'):
                    url = 'https://' + url
                urls.append(url)
        return urls

class WebCrawler:
    def __init__(self):
        self.results = []

    def crawl(self, q, result):
        while not q.empty():
            url = q.get()
            try:
                url_utf8 = url[1].encode('utf-8')
                res = requests.get(url_utf8, verify=False)
                logger.info(f'Searched home URL: {res.url}')

                if res.status_code != 200:
                    result[url[0]] = {}
                    logger.warning(f"{url[1]} Status code: {res.status_code}")
                    continue

                info = BeautifulSoup(res.content, 'lxml', from_encoding=res.encoding)
                emails_home = EmailPhoneExtractor.get_email(info.get_text())
                phones_home = EmailPhoneExtractor.get_phone(info.get_text())

                contacts_f = {'website': res.url, 'Email': '', 'Phone': ''}

                try:
                    contact_element = info.find('a', string=re.compile('contact', re.IGNORECASE))
                    if contact_element:
                        contact = contact_element.get('href')
                        if 'http' in contact:
                            contact_url = contact
                        else:
                            contact_url = res.url[0:-1] + "/" + contact

                        res_contact = requests.get(contact_url, verify=False)
                        contact_info = BeautifulSoup(res_contact.content, 'lxml', from_encoding=res_contact.encoding).get_text()

                        logger.info(f'Searched contact URL: {res_contact.url}')

                        emails_contact = EmailPhoneExtractor.get_email(contact_info)
                        phones_contact = EmailPhoneExtractor.get_phone(contact_info)

                        emails_f = emails_home + emails_contact
                        phones_f = phones_home + phones_contact

                    else:
                        emails_f = emails_home
                        phones_f = phones_home

                    emails_f = EmailPhoneExtractor.remove_dup_email(emails_f)
                    phones_f = EmailPhoneExtractor.remove_dup_phone(phones_f)

                    contacts_f['Email'] = emails_f[0] if emails_f else ''
                    contacts_f['Phone'] = phones_f[0] if phones_f else ''

                    result[url[0]] = contacts_f

                except Exception as e:
                    logger.error(f'Error in contact URL: {e}')
                    result[url[0]] = {}

            except Exception as e:
                logger.error(f"Request error in threads: {e}")
                result[url[0]] = {}
            finally:
                q.task_done()
                logger.debug(f"Queue task no {url[0]} completed.")
        return True

    def start_crawling(self, urls):
        q = Queue(maxsize=0)
        num_threads = min(50, len(urls))
        self.results = [{} for _ in urls]

        for i in range(len(urls)):
            q.put((i, urls[i]))

        for i in range(num_threads):
            logger.debug(f"Starting thread: {i}")
            worker = Thread(target=self.crawl, args=(q, self.results))
            worker.daemon = True
            worker.start()

        q.join()
        return self.results

class WebScraperApp:
    def __init__(self, url_file='web_urls.txt', output_file='websites_info.xlsx'):
        self.url_file = url_file
        self.output_file = output_file

    def run(self):
        urls = URLReader.read_file(self.url_file)
        crawler = WebCrawler()
        results = crawler.start_crawling(urls)
        df = pd.DataFrame(results)
        df.to_excel(self.output_file, index=False)

if __name__ == "__main__":
    app = WebScraperApp()
    app.run()
