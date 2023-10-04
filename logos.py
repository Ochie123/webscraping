import requests
url = 'http://www.webscrapingfordatascience.com/complexjavascript/'
my_cookies = {
    'nonce': '8894',
    'PHPSESSID': '3442vcsvpdojmcbomh9boqodki'
    }
r = requests.get(url + 'quotes.php', params={'p': '0'}, cookies=my_cookies)
print(r.text)
