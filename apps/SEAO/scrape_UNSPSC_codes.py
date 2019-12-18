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


def scrape_codes():
    # initialize dictionary to store UNSPSC code options as lists before merging as columns of data frame
    codes = {}
    # initialize empty lists for each column
    for col in ['segment', 'family', 'class', 'commodity']:
        codes[col] = []
    # define link with initial list of UNSPSC codes
    base_link = 'https://www.seao.ca/Recherche/ajouter_UNSPSC.aspx?' 
    # define function to standardize process for scraping UNSPSC codes from a table
    def collect(code):
        # visit page with respective list of UNSPSC codes
        browser.get(base_link + ('Code=' + code if code else ''))
        # pause
        time.sleep(1)
        # collect codes on page
        list_cells = browser.find_elements_by_xpath('//table[@class="'+IDS['category_table']+'"]/tbody/tr/td[2]')
        list_codes = [cell.find_element_by_tag_name('a').text for cell in list_cells]
        return list_codes
    # collect codes for each segment, family, class and commodity
    # TODO: remove [:2] when ready to do for all codes
    list_segments = collect(None)
    for s in list_segments[:2]:
        list_families = collect(s)
        for f in list_families[:2]:
            list_classes = collect(f)
            for c in list_classes[:2]:
                list_commodities = collect(c)
                codes['commodity'].extend(list_commodities)
                codes['class'].extend([c for i in range(len(list_commodities))])
                codes['family'].extend([f for i in range(len(list_commodities))])
                codes['segment'].extend([s for i in range(len(list_commodities))])
    # convert stored lists into dataframe and save as csv
    df_codes = pd.DataFrame(data=codes)
    print(df_codes)
    df_codes.to_csv('result_UNSPSC_codes.csv')
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
    IDS = ARGS.elements
    # define fields to scrape from listings
    FIELDS = ARGS.fields

    print('\n>>> Opening browser...')
    browser = open_browser()

    print('\n>>> Logging in...')
    login()

    print('\n>>> Gathering UNSPSC options...')
    scrape_codes()

    print('\n>>> Quitting browser...')
    quit_browser()