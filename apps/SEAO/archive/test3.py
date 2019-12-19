import json
import requests
from lxml import html
from bs4 import BeautifulSoup
from random import randint
from time import sleep

# note login details
payload = {
    "ctl00_ctl00_phContent_phLeftBigCol_UCLogin_txtUserCode": "watergeeks", 
	"ctl00_ctl00_phContent_phLeftBigCol_UCLogin_txtPassword": "Password!@#$",
	"ctl00_ctl00_phContent_phRightCol_UCLoginBox_txtUserCode": "watergeeks", 
	"ctl00_ctl00_phContent_phRightCol_UCLoginBox_txtPassword": "Password!@#$",
    "__EVENTVALIDATION": "/wEdAAevVXD1oYELeveMr0vHCmYPXu8srqJydQWz4+hMAnGgf04boAmMZhofdM3f8xqjxEemJWw597ZUFY8T47ZODwF4PoIzK/q7X4U3L98Q+aT7mcBI0YxtvUlFdhi4C0MPmdTfkatAn3mfSPnC61CZjy/lt+LvqcLt6zcZryZALdQlBvx9NGo="
}

# create session object
session_requests = requests.session()

# extract the csrf token from the web page
login_url = "https://www.seao.ca/Login.aspx"
page = session_requests.get(login_url, verify=False)

d = json.loads(page.text)
print(d)

# tree = html.fromstring(page.text)
# authenticity_token = list(set(tree.xpath("//input[@name='__EVENTVALIDATION']/@value")))[0]

# result = session_requests.post(
# 	login_url, 
# 	data = payload, 
# 	headers = dict(referer=login_url)
# )

sleep(randint(10,30))

# url = 'https://www.seao.ca/SEAO/monseao.aspx'
# result = session_requests.get(
# 	url, 
# 	data = payload, 
# 	headers = dict(referer=url)
# )

# soup = BeautifulSoup(result.content, 'html.parser')
# print(soup.prettify())

# tree = html.fromstring(result.content)
# bucket_names = tree.xpath("//a[@class='btnPrimaire']/text()")

# print(bucket_names)

# result.ok # Will tell us if the last request was ok
# result.status_code # Will give us the status from the last request