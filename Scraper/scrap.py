import time
import threading
import json
import re

from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import InvalidArgumentException, ElementNotInteractableException, StaleElementReferenceException, NoSuchElementException, WebDriverException, InvalidElementStateException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


RELIABLE_SITES = ["apnews.com"] #["apnews.com","nbcnews.com"]

class Bot():
    def __init__(self, x, y, h, issue):
        self.text = ""
        x = str(x)
        y = str(y)
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36"
        self.options = webdriver.ChromeOptions()
        if h:
            self.options.add_argument("--headless")
        self.options.add_argument(f'user-agent={user_agent}')
        self.options.add_argument("--window-size="+x+","+y)
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--allow-running-insecure-content')
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--proxy-server='direct://'")
        #print('--proxy-server='+PROXY)
        #self.options.add_argument('--proxy-server='+PROXY)
        self.options.add_argument("--proxy-bypass-list=*")
        self.options.add_argument("--start-maximized")
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--no-sandbox')
        self.options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.notifications": 1
        })
        #service = Service(executable_path=r'chromedriver')
        self.driver = webdriver.Chrome(options=self.options)

        self.issue = issue

    #
    # Basic functionality
    #
    def stop(self):
        self.driver.quit()
    def goto(self, url):
        self.site = url
        try:
            self.driver.get(url)
        except InvalidArgumentException:
            self.driver.get("https://"+url)
    def list_links(self):
        main = None
        if self.site == "nbcnews.com":
            main = self.driver.find_element(By.ID, "content")
        else:
            #apnews
            try:
                main = self.driver.find_element(By.TAG_NAME, "main")
            except NoSuchElementException:
                print("No disscernible link container. Stopping driver.")
                self.stop()
            
        elements = main.find_elements(By.TAG_NAME, "a")
        links = {}
        m = 10
        i = 0
        for l in elements:
            try:
                if l.text:
                    url = l.get_attribute("href")
                    pattern = r"https?://(?:www\.)?([a-zA-Z0-9-]+\.[a-zA-Z]+)"
                    match = re.match(pattern, url)
                    if match and match.group(1) == self.site:
                        if url not in links.keys():
                            i+=1
                            links[url] = l.text
                        
            except StaleElementReferenceException:
                pass
            if i == m:
                break
        return links
    def get_search(self):
        search = self.driver.find_element(By.NAME, "q")
        return search
    def type(self, element, text):
        #make all parent elements visible
        self.driver.execute_script("""
            var elem = arguments[0]; 
            while (elem) { 
                elem.style.display = 'block'; 
                elem.style.overflow = 'visible';
                elem = elem.parentElement; 
            }""", element)

        element.click()
        element.send_keys(text)
        element.send_keys(Keys.RETURN)

    #
    # Scraping scripts
    #
    #search the site for articles related to the issue
    def search_issue(self):
        search = self.get_search()
        self.type(search, self.issue)
        # Wait for the next page to load
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.staleness_of(search))
        self.links = self.list_links()
        return self.links
    
    def get_article(self, link):
        self.driver.get(link)
        text_elem = None

        if self.site == "apnews.com":
            try:
                text_elem = self.driver.find_elements(By.CLASS_NAME, "RichTextStoryBody")[0]
                self.text += self.driver.title + "\n\n" + text_elem.text + "\n\n"

            except IndexError:
                pass
    
    #
    # Get political position
    #
    def get_position(self, person):
        self.goto("isidewith.com")
        #go to person/policies
        #get policies


def run(bot):
    links = {}
    for site in RELIABLE_SITES:
        bot.goto(site)
        links = dict( links, ** bot.search_issue() )

    list_links_keys = list(links.keys())
    for x in range(len(list_links_keys)):
        bot.get_article(list_links_keys[x])

    time.sleep(5)
    bot.stop()
    print("Bot stopped.")


def start_thread(issue):
    bot = Bot(800,600,True,issue)

    thread = threading.Thread(target=lambda: run(bot))
    thread.start()

    return bot

def scrape(main_idea):
    bot = start_thread(main_idea)
    time.sleep(10) #make this longer if you need more time to get articles
    return bot.text

if __name__ == "__main__":
    issue = "immigration"
    bot = start_thread(issue)

    end = 'not_empty'
    while end != '':
        end = input("Enter to stop thread...\n\n")

    bot.stop()
    print("Thread stopped.")
