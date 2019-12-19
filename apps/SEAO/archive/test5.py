import requests
import lxml.html

html = requests.get('https://www.seao.ca/Login.aspx')
doc = lxml.html.fromstring(html.content)
result = doc.xpath()
