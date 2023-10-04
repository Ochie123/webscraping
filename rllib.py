import os
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from urllib.request import urlretrieve
import certifi
import ssl


ssl._create_default_https_context = ssl._create_unverified_context

def getAbsoluteURL(baseUrl, source):
    parsed_url = urlparse(source)
    if parsed_url.scheme and parsed_url.netloc:
        return source
    else:
        return urljoin(baseUrl, source)

def getDownloadPath(baseUrl, absoluteUrl, downloadDirectory):
    path = absoluteUrl.replace('www.', '')
    path = path.replace(baseUrl, '')
    path = downloadDirectory + path
    directory = os.path.dirname(path)
    
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    return path

baseUrl = 'https://www.sputtargets.com/'
downloadDirectory = 'downloads'

r = requests.get(baseUrl, stream=True)
html_contents = r.text
bs = BeautifulSoup(html_contents, 'html.parser')
downloadList = bs.find_all('img', src=True)  # Changed to find all <img> tags with src attribute

if len(downloadList) < 1:
    print("No images found")
else:
    top_image = downloadList[0]  # Get the first image from the list
    fileUrl = getAbsoluteURL(baseUrl, top_image['src'])
    if fileUrl is not None:
        print("Downloading:", fileUrl)
        urlretrieve(fileUrl, getDownloadPath(baseUrl, fileUrl, downloadDirectory))
    else:
        print('No link found')

print("Download completed!")
