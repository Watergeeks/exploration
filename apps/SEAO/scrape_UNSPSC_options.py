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
        codes[col+'_code'] = []
        codes[col+'_name'] = []
    # define link with initial list of UNSPSC codes
    base_link = 'https://www.seao.ca/Recherche/ajouter_UNSPSC.aspx?' 
    # define function to standardize process for scraping UNSPSC codes from a table
    def collect(code):
        # visit page with respective list of UNSPSC codes
        browser.get(base_link + ('Code=' + code if code else ''))
        # pause
        time.sleep(1)
        # collect codes and respective names on page
        cells_codes = browser.find_elements_by_xpath('//table[@class="'+IDS['category_table']+'"]/tbody/tr/td[2]')
        list_codes = [cell.find_element_by_tag_name('a').text for cell in cells_codes]
        cells_names = browser.find_elements_by_xpath('//table[@class="'+IDS['category_table']+'"]/tbody/tr/td[3]')
        list_names = [cell.find_element_by_tag_name('label').text for cell in cells_names]
        return list_codes, list_names
    # start recording time taken to scrape all segments
    print('\nRecording time to scrape each segment:')
    start_time = time.time()
    # collect codes for each segment, family, class and commodity 
    # TODO: remove [:2] when ready to do for all codes
    list_segment_codes, list_segment_names = collect(None)
    for i in range(len(list_segment_codes)):
        # refresh timer to record time to scrape next segment
        prev_time = time.time()
        # note segment code and name
        s_c = list_segment_codes[i]
        s_n = list_segment_names[i]
        list_family_codes, list_family_names = collect(s_c)
        for j in range(len(list_family_codes)):
            # note family code and name
            f_c = list_family_codes[j]
            f_n = list_family_names[j]
            list_class_codes, list_class_names = collect(f_c)
            for k in range(len(list_class_codes)):
                # note class code and name
                c_c = list_class_codes[k]
                c_n = list_class_names[k]
                list_commodity_codes, list_commodity_names = collect(c_c)
                codes['commodity_code'].extend(list_commodity_codes)
                codes['class_code'].extend([c_c for i in range(len(list_commodity_codes))])
                codes['family_code'].extend([f_c for i in range(len(list_commodity_codes))])
                codes['segment_code'].extend([s_c for i in range(len(list_commodity_codes))])
                codes['commodity_name'].extend(list_commodity_names)
                codes['class_name'].extend([c_n for i in range(len(list_commodity_names))])
                codes['family_name'].extend([f_n for i in range(len(list_commodity_names))])
                codes['segment_name'].extend([s_n for i in range(len(list_commodity_names))])
        # calculate time taken to scrape one segment
        delta_time = round(time.time() - prev_time, 4)
        print(s_c + ' ' + s_n + ': ' + str(delta_time) + ' seconds')
    # calculate time taken to scrape all segments
    delta_time = round(time.time() - start_time, 4)
    print('All UNSPSC options: ' + str(delta_time) + ' seconds')
    # convert stored lists into dataframe and save as csv
    df_codes = pd.DataFrame(data=codes)
    print('\nData frame for codes/names of all UNSPSC options')
    print(df_codes)
    df_codes.to_csv('result_UNSPSC_options.csv')
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