import requests 
from urllib.request import urlopen 
from urllib.error import HTTPError 
from urllib.error import URLError

baseUrl = 'http://www.pegdevelopment.com'


try:
    r = requests.get(baseUrl, stream=True)
except HTTPError as e:
    print(e)
except URLError as e:
    print('The server could not be found!')
else:
    print('It Worked!')
