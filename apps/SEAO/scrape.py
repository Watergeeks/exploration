import time
import argparse
import platform
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


def click_if_button_exists(id):
    try:
        browser.find_element_by_id(id).click()
    except NoSuchElementException:
        return False
    return True


if __name__ == '__main__':

    # define parser to parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-username', type=str, default='watergeeks', help='username')
    parser.add_argument('-password', type=str, default='Password!@#$', help='password')
    parser.add_argument('-searchany', type=str, default='"eau potable" "eaux usées"', help='search any of these keywords')
    parser.add_argument('-searchall', type=str, default='traitement', help='search all of these keywords')
    parser.add_argument('-searchnone', type=str, default='', help='search none of these keywords')
    args = parser.parse_args()

    # define element IDs
    ID = {
        'root': 'ctl00_ctl00_phContent_',
        'login_username': 'ctl00_ctl00_phContent_phLeftBigCol_UCLogin_txtUserCode',
        'login_password': 'ctl00_ctl00_phContent_phLeftBigCol_UCLogin_txtPassword',
        'login_button': 'ctl00_ctl00_phContent_phLeftBigCol_UCLogin_btnLogin',
        'login_session': 'ctl00_ctl00_phContent_UCMessageBox1_btnYes',
        'search_link': 'ctl00_ctl00_liAdvanced',
        'search_any': 'ctl00_ctl00_phContent_phLeftBigCol_ctl00_UcSearchJumelageKeyWords_anyKeywordsTextBox',
        'search_all': 'ctl00_ctl00_phContent_phLeftBigCol_ctl00_UcSearchJumelageKeyWords_allKeywordsTextBox',
        'search_none': 'ctl00_ctl00_phContent_phLeftBigCol_ctl00_UcSearchJumelageKeyWords_noneKeywordsTextBox',
        'search_button': 'ctl00_ctl00_phContent_phLeftBigCol_ctl00_searchAdv1Button'
    }

    # set path to chrome driver
    if platform.system() == 'Windows':
        CHROME_PATH = 'driver/chromedriver.exe'
    else:
        CHROME_PATH = 'driver/chromedriver'

    # open browser and set window size
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    browser = webdriver.Chrome(CHROME_PATH)
    browser.set_window_size(1366, 768)

    # visit login page and log in to redirect to dashboard
    browser.get('https://www.seao.ca/Login.aspx')
    browser.find_element_by_id(ID['login_username']).send_keys(args.username)
    browser.find_element_by_id(ID['login_password']).send_keys(args.password)
    browser.find_element_by_id(ID['login_button']).click()

    # pause
    time.sleep(2)

    # agree to renew session if asked
    click_if_button_exists(ID['login_session'])

    # pause
    time.sleep(2)

    # visit advanced search page
    browser.find_element_by_id(ID['search_link']).click()

    # pause
    time.sleep(2)

    # insert search criteria 
    browser.find_element_by_id(ID['search_any']).send_keys(args.searchany)
    browser.find_element_by_id(ID['search_all']).send_keys(args.searchall)
    browser.find_element_by_id(ID['search_button']).click()

    # pause
    time.sleep(10)

    # close browser
    browser.quit()
