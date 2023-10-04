import os 
import requests 
from urllib.parse import urlparse, urljoin 
from bs4 import BeautifulSoup
from urllib.request import urlopen 
from urllib.request import urlretrieve 
import json
from urllib.error import HTTPError 
from urllib.error import URLError
import certifi 
import ssl 

ssl._create_default_https_context= ssl._create_unverified_context 

headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
            'AppleWebKit 537.36 (KHTML, like Gecko) Chrome',
            'Accept':'text/html,application/xhtml+xml,application/xml;'
            'q=0.9,image/webp,*/*;q=0.8'}

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
        r = requests.get(baseUrl, headers=headers, stream=True, verify=False)
  
        html_contents = r.text 
        bs = BeautifulSoup(html_contents, 'html.parser') 
        downloadList = bs.find_all('img', src=True)  # Changed to find all <img> tags with src attribute 

        if len(downloadList) < 1: 
            print(f"No images found on {baseUrl}") 
        else: 
            top_image = downloadList[0]  # Get the first image from the list 
            fileUrl = getAbsoluteURL(baseUrl, top_image['src']) 
            if fileUrl is not None: 
                print(f" {fileUrl}") 
            else: 
                print(f"No link found on {baseUrl}")
    except HTTPError as e:
        print(e)
    except URLError as e:
        print('The server could not be found!')
       
 
print("Download completed!")
