from numpy import require
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

FILE_TYPE = 'ALL'

def get_res(links) :
    options = ['SUBS','ALL']
    all = ['480', '720', '1080', '2160']
    keys = {
        'SUBS' : -1,
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

def get_filetypes(links) :
    filetypes = ['ALL']
    for link in links :
        if '.' in link :
            filetypes.append(link.split('.')[-1])
    res = list(set(filetypes))
    try :
        res.remove('/')
    except :
        pass
    res.sort()
    return res

def get_link_file_type(links,FILE_TYPE) :
    res = []
    if FILE_TYPE == 'ALL' :
        return list(links)
    for link in links :
        if link.endswith(FILE_TYPE) :
            res.append(link)
    res.sort()
    return res

def get_links(links,option) :
    res = []
    if option == 'ALL' :
        return list(links)
    elif option == 'SUBS' :
        for link in links :
            if link.endswith('.srt') :
                res.append(link)
        return res
    for link in links :
        if option in link :
            res.append(link)
    return res

OUTPUT_FOLDER = f"output/"
FINAL_OUTPUT_FOLDER = f"{OUTPUT_FOLDER}/{time.strftime('%Y%m%d_%H%M%S')}/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36",
    "Accept": "*/*",
    
    }

def download(url,filename) :
    oFile = OUTPUT_FOLDER + filename
    block_size = 1024 #1 Kibibyte
    RESUME = False
    if os.path.exists(oFile+'.tmp'):
        outputFile = (oFile+'.tmp',"ab")
        existSize = os.path.getsize(oFile)
        headers["Range"] = "bytes=%s-" % (existSize)
        RESUME = True
    else:
        outputFile = (oFile'.tmp',"wb")
    response = requests.get(url,headers=headers,stream=True)
    total_size_in_bytes= int(response.headers.get('content-length', 0))

    if RESUME :
        print(f'\nResuming download for {filename} with {existSize}/{total_size_in_bytes}',end='')

    progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
    description = filename[:30]
    if len(description) < 30 :
        description += ' ' * (30 - len(description))
    progress_bar.set_description(description)
    with open(*outputFile) as file:
        for data in response.iter_content(block_size):
            if INTERRUPT :
                raise KeyboardInterrupt
            progress_bar.update(len(data))
            file.write(data)
        file.close()
        os.rename(oFile+'.tmp',FINAL_OUTPUT_FOLDER + filename)
    progress_bar.close()
    if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
        print("ERROR, something went wrong")

def download_video(links) :
    options = get_res(links)
    print(f'[+] Options:')
    for option in options:
        print(f'[{options.index(option):>2d}] {option}')

    try :
        option = options[int(input('[+] Choose an option: '))]
    except ValueError as e:
        print('[-] Invalid option')
        option = 'ALL'
    except IndexError as e:
        print('[-] Invalid option')
        option = 'ALL'
    except KeyboardInterrupt as e:
        print('[-] Interrupt')
        INTERRUPT = True
        sys.exit(0)

    required_links = get_links(links,option)
    required_links.insert(0,'ALL')
    for link in required_links:
        print(f'[+] {required_links.index(link):>2d} : {link}')
    required_links.remove('ALL')

    return required_links

def download_file(links) :
    required_links = links
    required_links.insert(0,'ALL')
    for link in required_links:
        print(f'[+] {required_links.index(link):>2d} : {link}')
    required_links.remove('ALL')

    return required_links

if __name__ == '__main__':
    try :
        URL = sys.argv[1]
    except :
        URL = "https://dl3.3rver.org/cdn2/03/series/2017/Money.Heist/S03/"
    print(f'URL: {URL}')
    req = Request(URL, headers=headers)
    html_page = urlopen(req)
    soup = BeautifulSoup(html_page,features="html.parser")

    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
    
    if not os.path.exists(FINAL_OUTPUT_FOLDER):
        os.makedirs(FINAL_OUTPUT_FOLDER)

    links = []
    l = {}
    for link in soup.findAll('a'):
        tLink = link.get('href')
        if tLink is not None and '.htm' not in tLink :
            links.append(tLink)
            l[tLink] = link.text

    availableFileTypes = get_filetypes(links)

    print(f'[+] Available file types:')
    for fileType in availableFileTypes:
        print(f'[{availableFileTypes.index(fileType):>2d}] {fileType}')
    
    try :
        FILE_TYPE = availableFileTypes[int(input('[+] Choose an option: '))]
    except ValueError as e:
        print('[-] Invalid option')
        FILE_TYPE = 'ALL'
    except IndexError as e:
        print('[-] Invalid option')
        FILE_TYPE = 'ALL'
    except KeyboardInterrupt as e:
        print('[-] Interrupt')
        INTERRUPT = True
        sys.exit(0)

    print(f'[+] File type: {FILE_TYPE}')

    links = get_link_file_type(links,FILE_TYPE)

    if FILE_TYPE == 'mkv' or FILE_TYPE == 'mp4' :
        required_links = download_video(links)
    else :
        required_links = download_file(links)

    try :
        x = int(input('[+] File to download :'))
        if x == 0 :
            filesToDownload = required_links
        else :
            filesToDownload = [required_links[x]]
    except ValueError as e :
        print('[-] Invalid option')
        filesToDownload = required_links
    except IndexError as e :
        print('[-] Invalid option')
        filesToDownload = required_links
    except KeyboardInterrupt as e :
        print('[-] Interrupt')
        print('[-] Exiting')
        sys.exit(0)
    except Exception as e :
        raise

    print(f'[+] Downloading {len(required_links)} files')

    processList = []
    threadList = []

    for link in filesToDownload:
        if 'ftp' in link :
            l = link
            filename = l.split('/')[-1]
        else :
            l = URL + link
            filename = link
        t = Thread(target=download, args=(l,filename,))
        t.start()
        threadList.append(t)
    
    for t in threadList:
        t.join()