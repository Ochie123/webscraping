#download and decode letters from images
import os
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from urllib.request import urlretrieve
import json
import ssl
from datetime import datetime
from OpenSSL import crypto
from PIL import Image
import pytesseract
import cairosvg

pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'

ssl._create_default_https_context = ssl._create_unverified_context

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit 537.36 (KHTML, like Gecko) Chrome",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
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

def is_logo_image(img_tag, baseUrl):
    top_image = img_tag
    fileUrl = getAbsoluteURL(baseUrl, top_image['src'])
    local_image_path = getDownloadPath(baseUrl, fileUrl, downloadDirectory)
    urlretrieve(fileUrl, local_image_path)  # Download the image

    
    with Image.open(local_image_path) as img:
        width, height = img.size
        if width >= MIN_LOGO_WIDTH and height >= MIN_LOGO_HEIGHT:
            return True
        else:
            return False

# Load URLs from JSON file
with open('/Users/patrick/Desktop/webscraping/local_businesses.json') as json_file:
    websites_data = json.load(json_file)

MIN_LOGO_WIDTH = 100  # Set your desired minimum logo width
MIN_LOGO_HEIGHT = 100  # Set your desired minimum logo height

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
                r = requests.get(baseUrl, stream=True, headers=headers, verify=True)
                r.raise_for_status()
                html_contents = r.text
                bs = BeautifulSoup(html_contents, 'html.parser')
                downloadList = bs.find_all('img', src=True)

                if len(downloadList) < 1:
                    print(f"No images found on {baseUrl}")
                else:
                    for img_tag in downloadList:
                        if is_logo_image(img_tag, baseUrl):
                            fileUrl = getAbsoluteURL(baseUrl, img_tag['src'])
                            if fileUrl is not None:
                                print(f"Downloading from {baseUrl}: {fileUrl}")
                                local_image_path = getDownloadPath(baseUrl, fileUrl, downloadDirectory)
                                urlretrieve(fileUrl, local_image_path)  # Download the image

                                # Handle SVG images by converting them to PNG
                                if fileUrl.lower().endswith('.svg'):
                                    png_path = local_image_path.replace('.svg', '.png')
                                    cairosvg.svg2png(url=fileUrl, write_to=png_path)

                                    with Image.open(png_path) as img:
                                        width, height = img.size
                                        print(f"Image size: {width}x{height}")

                                        logo_text = pytesseract.image_to_string(img)
                                        print(f"Extracted text from logo: {logo_text}")

                                        user_input = input("Do you want to use this logo? (yes/no): ")
                                        if user_input.lower() == "yes":
                                            # Do something with the selected logo
                                            pass
                                        else:
                                            # Continue with the next logo
                                            pass
                                else:
                                    with Image.open(local_image_path) as img:
                                        width, height = img.size
                                        print(f"Image size: {width}x{height}")

                                        logo_text = pytesseract.image_to_string(img)
                                        print(f"Extracted text from logo: {logo_text}")

                                        user_input = input("Do you want to use this logo? (yes/no): ")
                                        if user_input.lower() == "yes":
                                            # Do something with the selected logo
                                            pass
                                        else:
                                            # Continue with the next logo
                                            pass

        except ssl.SSLError as e:
            print(f"SSL Error for {baseUrl}: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Request Error for {baseUrl}: {e}")

print("Download and analysis completed!")
