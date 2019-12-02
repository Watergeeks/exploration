import time
import argparse
import platform
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select
import pandas as pd


def check_if_element_exists(id):
    try:
        browser.find_element_by_id(id)
    except NoSuchElementException:
        return False
    return True


def click_if_element_exists(id):
    if check_if_element_exists(id):
        browser.find_element_by_id(id).click()


def get_links(links):
    results = browser.find_element_by_id(ID['results_table']).find_elements_by_tag_name('tr')
    for row in results[1:]:
        links.append(row.find_elements_by_tag_name('td')[1].find_element_by_tag_name('a').get_attribute('href'))
    print(len(links))
    return links


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
        'search_button': 'ctl00_ctl00_phContent_phLeftBigCol_ctl00_searchAdv1Button',
        'results_sort': 'PublishedOpportunitySortByDropDown',
        'results_limit': 'PublishedOpportunityResultsPerPageDropDown',
        'results_button': 'PublishedOpportunitySortbtn',
        'results_next': 'PageNext',
        'results_table': 'tblResults',
        'listing_title': 'lbOppTitle',
        'listing_type': 'lbOppType',
        'listing_contract_type': 'lbContractType',
        'listing_date_publication': 'lbPublicationDateText',
        'listing_date_conclusion': 'lblAdjDate',
        'listing_date_complaints': 'lblDeadlineReceiptComplaintsDate',
        'listing_organization': 'lbOrganisation',
        'listing_address': 'OrganizationAddressTextvalue',
        'listing_contact': None,
        'listing_website': None,
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
    time.sleep(1)

    # agree to renew session if asked
    click_if_element_exists(ID['login_session'])

    # pause
    time.sleep(1)

    # visit advanced search page
    browser.find_element_by_id(ID['search_link']).click()

    # pause
    time.sleep(1)

    # insert search criteria 
    browser.find_element_by_id(ID['search_any']).send_keys(args.searchany)
    browser.find_element_by_id(ID['search_all']).send_keys(args.searchall)
    browser.find_element_by_id(ID['search_button']).click()
    
    # pause
    time.sleep(1)

    # increase number of listings per page and sort listings by category
    Select(browser.find_element_by_id(ID['results_sort'])).select_by_visible_text('Catégorie')
    Select(browser.find_element_by_id(ID['results_limit'])).select_by_visible_text('100')
    browser.find_element_by_id(ID['results_button']).click()

    # pause
    time.sleep(2)

    # initialize dictionary to store listing data as lists for each field before merging as columns of data frame
    listing = {}
    # note what fields to collect listing data for
    # TODO: consider what fields to include/exclude (here and in dictionary of IDs)
    fields = ['link', 'title', 'type', 'contract_type', 'date_publication', 'date_conclusion', 'date_complaints', 'organization', 'address']
    # initialize empty lists for each field in dictionary
    for field in fields:
        listing[field] = []

    # get links from table of search results from first page
    listing['link'] = get_links(listing['link'])
    # get links from table of search results from every next page
    while browser.find_element_by_id(ID['results_next']).get_attribute('style') != 'display: none;':
        # visit next page
        browser.get(browser.find_element_by_id(ID['results_next']).get_attribute('href'))
        # pause
        time.sleep(2)
        # get links for curent page
        listing['link'] = get_links(listing['link'])

    print()
    print('STATUS: gathered links to ' + str(len(listing['link'])) + ' listings from each page of search results')
    print()

    # TODO: change to visit all links instead of just 5 when ready
    for link in listing['link'][:5]:
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
        # do something # TODO: change actions here!
        print(link)
        # pause
        time.sleep(1)
        # close active window
        browser.close()
        # switch back to original window
        browser.switch_to.window(browser.window_handles[0])

    print()
    # TODO: change status when accomplished
    # print('STATUS: collected data from ' + str(len(listing['link'])) + ' listings')
    print('STATUS: visited ' + str(len(listing['link'])) + ' listings') 
    print()

    # pause
    time.sleep(1)

    # close browser
    # browser.quit()