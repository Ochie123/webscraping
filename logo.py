import os
import requests
from urllib.request import urlopen, urlretrieve
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import ssl
import warnings

ssl._create_default_https_context = ssl._create_unverified_context

def getAbsoluteURL(baseUrl, source):
    if source.startswith('http://www.'):
        url = 'http://{}'.format(source[11:])
    elif source.startswith('http://'):
        url = source
    elif source.startswith('www.'):
        url = 'http://{}'.format(source[4:])
    else:
        url = '{}{}'.format(baseUrl, source)
    
    if baseUrl not in url:
        return None
    
    return url

def getDownloadPath(baseUrl, absoluteUrl, downloadDirectory):
    path = absoluteUrl.replace('www.', '')
    path = path.replace(baseUrl, '')
    path = downloadDirectory + path
    directory = os.path.dirname(path)
    
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    return path

baseUrl = 'http://www.s.com'
downloadDirectory = 'downloads'

r = requests.get(baseUrl, stream=True)


html_contents = r.text
bs = BeautifulSoup(html_contents, 'html.parser')
downloadList = bs.div.find_all(src=True)

for download in downloadList:
     fileUrl = getAbsoluteURL(baseUrl, download['src'])
     if fileUrl is not None:
        print(fileUrl)
        print(downloadDirectory)
     else:
        print('no link found')
            
        
urlretrieve(fileUrl, getDownloadPath(baseUrl, fileUrl, downloadDirectory))



