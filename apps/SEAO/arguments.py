import sys
import os
import time
import argparse
import platform
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select
import pandas as pd


class Arguments():
    def __init__(self):
        self.username = 'watergeeks'
        self.password = 'Password!@#$'
        self.searchany = '"eau potable" "eaux usées"'
        self.searchall = 'traitement'
        self.searchnone = ''
        # TODO: consider what fields to include/exclude
        self.fields = ['link', 'title', 'type', 'contract_type', 
                       'date_publication', 'date_conclusion', 'date_complaints', 'organization', 'address', 
                       'class_code', 'class_name', 'category_code', 'category_name']
        # TODO: ensure respective element ID for fields are listed here as 'listing_<field>'
        self.elements = {
            'root': 'ctl00_ctl00_phContent_',
            'login_username': 'ctl00_ctl00_phContent_phLeftBigCol_UCLogin_txtUserCode',
            'login_password': 'ctl00_ctl00_phContent_phLeftBigCol_UCLogin_txtPassword',
            'login_button': 'ctl00_ctl00_phContent_phLeftBigCol_UCLogin_btnLogin',
            'login_session': 'ctl00_ctl00_phContent_UCMessageBox1_btnYes',
            'search_link': 'ctl00_ctl00_liAdvanced',
            'search_any': 'ctl00_ctl00_phContent_phLeftBigCol_ctl00_UcSearchJumelageKeyWords_anyKeywordsTextBox',
            'search_all': 'ctl00_ctl00_phContent_phLeftBigCol_ctl00_UcSearchJumelageKeyWords_allKeywordsTextBox',
            'search_none': 'ctl00_ctl00_phContent_phLeftBigCol_ctl00_UcSearchJumelageKeyWords_noneKeywordsTextBox',
            'search_class_codes_button1': 'UNSPSCCriteriaToggleImage',
            'search_class_codes_button2': 'ctl00_ctl00_phContent_phLeftBigCol_ctl00_UCSearchAdvanceOtherCriteriaPlusA1_UNSPSCAddLinkButton',
            'search_button': 'ctl00_ctl00_phContent_phLeftBigCol_ctl00_searchAdv1Button',
            'category_table': 'tblFondColore',
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
            'listing_tags': 'pnlUNSPSC', 
            'listing_class_code': 'UNSPSC_Code',
            'listing_class_name': 'UNSPSC_Desc',
            'listing_category_code': 'Label4',
            'listing_category_name': 'Label5'
        }
