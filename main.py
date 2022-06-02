import time
import sys
import os

from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import re

import requests

url = "https://dl3.3rver.org/cdn2/03/series/2017/Money.Heist/S03"
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

for link in l:
    if link.endswith('.mp4'):
        print(f'[+] {l[link]}')