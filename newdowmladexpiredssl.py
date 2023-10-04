import os
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from urllib.request import urlretrieve
import urllib3
import json
import certifi
import ssl
import warnings

ssl._create_default_https_context = ssl._create_unverified_context
# Disable SSL certificate verification warnings
warnings.filterwarnings("ignore", category=urllib3.exceptions.InsecureRequestWarning)

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

# Load URLs from JSON file
with open('/Users/patrick/Desktop/webscraping/local_businesses.json') as json_file:
    websites_data = json.load(json_file)

for website in websites_data:
    baseUrl = website['url']
    downloadDirectory = 'downloads'

    try:
        r = requests.get(baseUrl, stream=True,verify=False)
        html_contents = r.text
        bs = BeautifulSoup(html_contents, 'html.parser')
        downloadList = bs.find_all('img', src=True)  # Changed to find all <img> tags with src attribute
    except requests.exceptions.SSLError as e:
        print(f"SSL Certificate Error for {baseUrl}: {str(e)}")
        continue
    
    if len(downloadList) < 1:
        print(f"No images found on {baseUrl}")
    else:
        top_image = downloadList[0]  # Get the first image from the list
        fileUrl = getAbsoluteURL(baseUrl, top_image['src'])
        if fileUrl is not None:
            print(f"Downloading from {baseUrl}: {fileUrl}")
            urlretrieve(fileUrl, getDownloadPath(baseUrl, fileUrl, downloadDirectory))
        else:
            print(f"No link found on {baseUrl}")

print("Download completed!")
