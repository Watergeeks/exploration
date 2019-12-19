import platform
import time
from selenium import webdriver

if platform.system() == 'Windows':
    CHROME_PATH = 'driver/chromedriver.exe'
else:
    CHROME_PATH = 'driver/chromedriver'

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
browser = webdriver.Chrome(CHROME_PATH)
browser.set_window_size(1366, 768)
browser.get("https://www.seao.ca/Login.aspx")

browser.find_element_by_id("ctl00_ctl00_phContent_phLeftBigCol_UCLogin_txtUserCode").send_keys('watergeeks')
browser.find_element_by_id("ctl00_ctl00_phContent_phLeftBigCol_UCLogin_txtPassword").send_keys('Password!@#$')
browser.find_element_by_id("ctl00_ctl00_phContent_phLeftBigCol_UCLogin_btnLogin").click()
time.sleep(5)

html = browser.page_source
print(html)