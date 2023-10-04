#download images from a csv list of websites
import os
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from urllib.request import urlretrieve
import json
import ssl
from datetime import datetime
from OpenSSL import crypto

ssl._create_default_https_context = ssl._create_unverified_context

headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit 537.36 (KHTML, like Gecko) Chrome",
           "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
           }

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

# Load URLs from a JSON file
with open('/path/to/your/file') as json_file:
    websites_data = json.load(json_file)

for website in websites_data:
    baseUrl = website['url']
    downloadDirectory = 'downloads'

    try:
        hostname = urlparse(baseUrl).hostname
        try:
            cert = ssl.get_server_certificate((hostname, 443), ssl_version=ssl.PROTOCOL_TLS)
            x509 = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
            cert_validity_end = x509.get_notAfter().decode('utf-8')
            
            # Convert the expiration date to a timestamp
            cert_validity_end_timestamp = datetime.strptime(cert_validity_end, '%Y%m%d%H%M%SZ').timestamp()
            current_time = datetime.utcnow().timestamp()

            if current_time > cert_validity_end_timestamp:
                print(f"SSL certificate for {baseUrl} has expired. Ignoring SSL verification.")
                r = requests.get(baseUrl, stream=True, headers=headers, verify=False)  # Ignore SSL verification
            else:
                r = requests.get(baseUrl, stream=True, headers=headers, verify=True)  # Verify SSL certificate

                r.raise_for_status()  # Raise an exception for unsuccessful responses

            html_contents = r.text
            bs = BeautifulSoup(html_contents, 'html.parser')
            downloadList = bs.find_all('img', src=True)  # Find all <img> tags with src attribute

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
        except ssl.SSLError as e:
            print(f"SSL Error for {baseUrl}: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Request Error for {baseUrl}: {e}")

print("Download completed!")
