import requests
from bs4 import BeautifulSoup

url = 'https://kaiandkaro.com'  # Replace with the target website's URL
response = requests.get(url)
html_content = response.text

soup = BeautifulSoup(html_content, 'html.parser')

# Use CSS selectors or other methods to locate the logo image tag
logo_image = soup.find('img', alt='Logo', type='image/x-icon')  # Example selector, adjust as needed

if logo_image is not None:
    logo_url = logo_image['src']
    
    logo_response = requests.get(logo_url, stream=True)
    if logo_response.status_code == 200:
        with open('logo.jpg', 'wb') as image_file:
            for chunk in logo_response.iter_content(1024):
                image_file.write(chunk)
else:
    print("Logo image not found.")