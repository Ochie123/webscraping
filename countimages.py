#count images
import requests

from bs4 import BeautifulSoup
url = 'http://www.archive.org'

r = requests.get(url)
html_contents = r.text
bs = BeautifulSoup(html_contents, 'html.parser')

image = bs.div.find_all(['img', 'src' ])
print(len(image))
