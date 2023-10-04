import requests
from bs4 import BeautifulSoup
import datetime
import random
import re



def getLinks(articleUrl):
    url = 'http://en.wikipedia.org{}'.format(articleUrl)
    r = requests.get(url)
    html_contents = r.text
    bs = BeautifulSoup(html_contents, 'html.parser')
    return bs.find('div', {'id':'bodyContent'}).find_all('a',
        href=re.compile('^(/wiki/)((?!:).)*$'))


links = getLinks('/wiki/Kevin_Bacon')
while len(links) > 0:
    newArticle = links[random.randint(0, len(links)-1)].attrs['href']
    print(newArticle)
    links = getLinks(newArticle)




