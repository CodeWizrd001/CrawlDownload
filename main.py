import time
import tqdm
import sys
import os

from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import re

import requests

def get_res(links) :
    options = ['ALL']
    all = ['480', '720', '1080', '2160']
    keys = {
        'ALL' : 0,
        '480' : 1,
        '720' : 2,
        '1080' : 3,
        '2160' : 4
    }
    for link in links :
        for option in all :
            if option in link :
                options.append(option)
    options = list(set(options))
    options.sort(key=keys.get)
    return options

def get_links(links,option) :
    res = []
    if option == 'ALL' :
        return list(links)
    for link in links :
        if option in link :
            res.append(link)
    return res

OUTPUT_FOLDER = "output/"

url = "https://dl3.3rver.org/cdn2/03/series/2017/Money.Heist/S03/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36"
    }

req = Request(url, headers=headers)
html_page = urlopen(req)
soup = BeautifulSoup(html_page,features="html.parser")

# r=requests.get(url, headers=headers)
# soup = BeautifulSoup(r.content, "html5lib")


links = []
l = {}
for link in soup.findAll('a'):
    links.append(link.get('href'))
    l[link.get('href')] = link.text

options = get_res(links)

print(f'[+] Options:')
for option in options:
    print(f'[{options.index(option):>2d}] {option}')

try :
    option = options[int(input('[+] Choose an option: '))]
except :
    print('[-] Invalid option')
    option = 'ALL'

required_links = get_links(links,option)

for link in required_links:
    if link.endswith('.mp4') or link.endswith('.mkv'):
        print(f'[+] {l[link]}')

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

f = required_links[0]
