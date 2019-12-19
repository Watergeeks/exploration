from arguments import *


def check_if_element_exists(id):
    try:
        browser.find_element_by_id(id)
    except NoSuchElementException:
        return False
    return True


def open_browser():
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
    return browser


def login():
    # visit login page and log in to redirect to dashboard
    browser.get('https://www.seao.ca/Login.aspx')
    browser.find_element_by_id(IDS['login_username']).send_keys(ARGS.username)
    browser.find_element_by_id(IDS['login_password']).send_keys(ARGS.password)
    browser.find_element_by_id(IDS['login_button']).click()
    # pause
    time.sleep(1)
    # agree to renew session if asked
    if check_if_element_exists(IDS['login_session']):
        browser.find_element_by_id(IDS['login_session']).click()
    # pause
    time.sleep(1)


def search_listings():
        # visit advanced search page
        browser.find_element_by_id(IDS['search_link']).click()
        # pause
        time.sleep(1)
        # insert search criteria 
        browser.find_element_by_id(IDS['search_any']).send_keys(ARGS.searchany)
        browser.find_element_by_id(IDS['search_all']).send_keys(ARGS.searchall)
        browser.find_element_by_id(IDS['search_button']).click()
        # TODO: finish working out how to retrieve desired UNSPSC codes
        # # toggle search box for UNSPSC codes 
        # browser.find_element_by_id(IDS['search_class_codes_button1']).click()
        # # pause
        # time.sleep(1)
        # # check initial list of UNSPSC codes
        # browser.find_element_by_id(IDS['search_class_codes_button2']).click()
        # # ...
        # pause
        time.sleep(1)
        # increase number of listings per page and sort listings by category
        Select(browser.find_element_by_id(IDS['results_sort'])).select_by_visible_text('Catégorie')
        Select(browser.find_element_by_id(IDS['results_limit'])).select_by_visible_text('100')
        browser.find_element_by_id(IDS['results_button']).click()
        # pause
        time.sleep(2)


def scrape_listings():
    return ''


def quit_browser():
    # pause
    time.sleep(1)
    # close browser
    browser.quit()


if __name__ == '__main__':

    print('\n>>> Defining constant arguments...')
    # define user arguments
    ARGS = Arguments()
    # define element IDs
    IDS = ARGS.elements
    # define fields to scrape from listings
    FIELDS = ARGS.fields

    print('\n>>> Opening browser...')
    browser = open_browser()

    print('\n>>> Logging in...')
    login()

    print('\n>>> Searching for listings based on given criteria...')
    search_listings()

    print('\n>>> Gathering data from listings in search results...')
    scrape_listings()

    print('\n>>> Quitting browser...')
    quit_browser()