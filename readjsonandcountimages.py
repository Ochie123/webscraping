import requests
from bs4 import BeautifulSoup
import json

# Read JSON data from file
with open('/Users/patrick/Desktop/local_businesses.json') as json_file:
    data = json.load(json_file)

for entry in data:
    name = entry['name']
    url = entry['url']

    r = requests.get(url)
    html_contents = r.text
    bs = BeautifulSoup(html_contents, 'html.parser')

    image_lengths = []

    for img in bs.find_all('img'):
        image_url = img.get('src')
        if image_url.startswith(('http://', 'https://')):
            image_response = requests.get(image_url)
            image_length = len(image_response.content)
            image_lengths.append(image_length)

    print(f"Name: {name}")
    print(f"URL: {url}")
    print(f"Total Images: {len(image_lengths)}")
    print(f"Total Image Lengths: {sum(image_lengths)} bytes")
    print("-" * 30)
