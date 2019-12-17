from arguments import *

def main(ARGS, IDS, FIELDS):

    def check_if_element_exists(id):
        try:
            browser.find_element_by_id(id)
        except NoSuchElementException:
            return False
        return True

    def get_links(links):
        results = browser.find_element_by_id(IDS['results_table']).find_elements_by_tag_name('tr')
        for row in results[1:]:
            links.append(row.find_elements_by_tag_name('td')[1].find_element_by_tag_name('a').get_attribute('href'))
        return links

    def open_browser():
        # set path to chrome driver
        if os.name == 'nt':
            CHROME_PATH = os.path.join(sys.executable, 'driver', 'chromedriver.exe')
        else:
            CHROME_PATH = os.path.join('driver', 'chromedriver')
        # if platform.system() == 'Windows':
        #     CHROME_PATH = os.path.join('driver', 'chromedriver.exe')
        # else:
        #     CHROME_PATH = os.path.join('driver', 'chromedriver')
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

    def search():
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
    
    print('\n>>> Opening browser...')
    browser = open_browser()
    print('\n>>> Logging in...')
    login()
    print('\n>>> Searching...')
    search()
    print('\n>>> Gathering links of listings...')

    # initialize dictionary to store listing data as lists for each field before merging as columns of data frame
    listing = {}
    # initialize empty lists for each field in dictionary
    for field in FIELDS:
        listing[field] = []

    # get links from table of search results from first page
    listing['link'] = get_links(listing['link'])
    # get links from table of search results from every next page
    while browser.find_element_by_id(IDS['results_next']).get_attribute('style') != 'display: none;':
        # visit next page
        browser.get(browser.find_element_by_id(IDS['results_next']).get_attribute('href'))
        # pause
        time.sleep(2)
        # get links for curent page
        listing['link'] = get_links(listing['link'])

    print('\nSTATUS: gathered links to ' + str(len(listing['link'])) + ' listings from each page of search results\n')

    # TODO: temporarily reduce length of links list to 2 for test
    # listing['link'] = listing['link'][:2]
    for link in listing['link']:
        # pause
        time.sleep(1)
        # open new tab, does not switch to new window
        browser.execute_script('window.open("");')
        # switch to new window
        browser.switch_to.window(browser.window_handles[1])
        # visit respective link
        browser.get(link)
        # pause
        time.sleep(1)
        # store information from desired fields
        for f in FIELDS[1:]:
            if f in ['class_code', 'class_name', 'category_code', 'category_name']:
                list_values = browser.find_elements_by_xpath('//div[@id="'+IDS['listing_tags']+'"]/div/div/ul/li/span[@id="'+IDS['listing_'+f]+'"]')
                list_values = [value.text for value in list_values]
                listing[f].append(list_values)
            else:
                if check_if_element_exists(IDS['listing_'+f]):
                    value = browser.find_element_by_id(IDS['listing_'+f]).text
                    listing[f].append(value)
                else:
                    listing[f].append(None)
        # pause
        time.sleep(1)
        # close active window
        browser.close()
        # switch back to original window
        browser.switch_to.window(browser.window_handles[0])

    # convert stored lists into dataframe
    results = pd.DataFrame(data=listing)
    print(results)
    results.to_csv('results.csv')

    print('\nSTATUS: collected data from ' + str(len(listing['link'])) + ' listings\n')

    # pause
    time.sleep(1)

    # close browser
    browser.quit()


if __name__ == '__main__':
    # define user arguments
    ARGS = Arguments()
    # define element IDs
    IDS = ARGS.ids
    # define fields to scrape from listings
    FIELDS = ARGS.fields
    # run main method
    main(ARGS, IDS, FIELDS) 