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


def collect():
    # initialize empty list of codes
    list_codes = []
    # visit page with initial list of UNSPSC codes
    browser.get('https://www.seao.ca/Recherche/ajouter_UNSPSC.aspx?')
    # pause
    time.sleep(1)
    # TODO: do something with ID['category_table']
    list_cells = browser.find_elements_by_xpath('//table[@class="'+IDS['category_table']+'"]/tbody/tr/td[2]')
    # list_links = [cell.find_element_by_tag_name('a').get_attribute('href') for cell in list_cells]
    list_codes = [cell.find_element_by_tag_name('a').text for cell in list_cells]
    print(list_codes)
    # pause
    time.sleep(2)


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
    IDS = ARGS.ids
    # define fields to scrape from listings
    FIELDS = ARGS.fields

    print('\n>>> Opening browser...')
    browser = open_browser()

    print('\n>>> Logging in...')
    login()

    print('\n>>> Gathering UNSPSC options...')
    collect()

    print('\n>>> Quitting browser...')
    #quit_browser()