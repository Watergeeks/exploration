import requests
from lxml import html
from bs4 import BeautifulSoup

# note login details
payload = {
	"username": "<USER NAME>", 
	"password": "<PASSWORD>", 
	"csrfmiddlewaretoken": "<CSRF_TOKEN>"
}

# create session object
session_requests = requests.session()

# extract the csrf token from the web page
login_url = "https://bitbucket.org/account/signin/?next=/"
result = session_requests.get(login_url)

tree = html.fromstring(result.text)
#authenticity_token = list(set(tree.xpath("//input[@name='csrfmiddlewaretoken']/@value")))[0]

# result = session_requests.post(
# 	login_url, 
# 	data = payload, 
# 	headers = dict(referer=login_url)
# )

soup = BeautifulSoup(result.content, 'html.parser')
print(soup.prettify())