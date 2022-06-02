from tqdm import tqdm
import time
import sys
import os

from multiprocessing import Process, Queue
from threading import Thread

from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import re

import requests

INTERRUPT = False

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

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36"
    }

def download(url,filename) :
    oFile = OUTPUT_FOLDER + filename
    block_size = 1024 #1 Kibibyte
    if os.path.exists(oFile):
        outputFile = (oFile,"ab")
        existSize = os.path.getsize(oFile)
        headers["Range"] = "bytes=%s-" % (existSize)
        print(f'\nResuming download for {filename} from {existSize}',end='')
    else:
        outputFile = (oFile,"wb")
    response = requests.get(url,headers=headers,stream=True)
    total_size_in_bytes= int(response.headers.get('content-length', 0))

    progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
    progress_bar.set_description(filename)
    with open(*outputFile) as file:
        for data in response.iter_content(block_size):
            if INTERRUPT :
                raise KeyboardInterrupt
            progress_bar.update(len(data))
            file.write(data)
        file.close()
    progress_bar.close()
    if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
        print("ERROR, something went wrong")

if __name__ == '__main__':
    try :
        URL = sys.argv[1]
    except :
        URL = "https://dl3.3rver.org/cdn2/03/series/2017/Money.Heist/S03/"
    print(f'URL: {URL}')
    req = Request(URL, headers=headers)
    html_page = urlopen(req)
    soup = BeautifulSoup(html_page,features="html.parser")

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

    print(f'[+] Downloading {len(required_links)} files')

    processList = []
    threadList = []

    for link in required_links:
        l = URL + link
        filename = link
        t = Thread(target=download, args=(l,filename,))
        t.start()
        threadList.append(t)
    
    for t in threadList:
        t.join()