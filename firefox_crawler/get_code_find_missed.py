import time
import datetime

import json

import dateutil.parser as dparser

import os
import shutil
import urllib.request
import ssl
ssl._create_default_https_context = ssl._create_unverified_context


def find_missed(new_file, old_file):
    """Find missed extensions in the new list.
    Retrieves CRX (Chrome extension file) specified by ext_id from Chrome Web
    Store, into directory specified by dst.
    Args:
        new_file: file path of the new extension list 
        old_file: file path of the last extension list
    Returns:
        missed_item:
        missed_id:
    """
    new_list = []
    old_list = []
    missed_item = []
    missed_id = []
    with open(new_file) as json_file:
        new_list = json.load(json_file)
    with open(old_file) as json_file:
        old_list = json.load(json_file)
    for item in old_list:
        item_id = item["id"]
        isMissed = True
        for new_item in new_list:
            if new_item["id"] == item_id:
                isMissed = False
                break
        if isMissed:
            missed_item.append(item)
            missed_id.append(item_id)
    return [missed_item, missed_id]

# store missed App list in '/missed.json'


def handle_missed_list(missed_item, missed_file):
    current_time=datetime.datetime.now()
    missed_list = []
    if 0 != os.path.getsize(missed_file):
        with open(missed_file,'r') as json_file:
            missed_list = json.load(json_file)
        for i in missed_item:
            missed_list.append(i)

    else:
        missed_list = missed_item

    for item in missed_list:
        item["missed_date"]=current_time.strftime("%Y-%m-%d %H:%M:%S")

    with open(missed_file, "w") as json_file:
        json.dump(missed_list, json_file)

# move missed App source code from '/recent' to 'missed'


def handle_missed_file(missed_id, missed_dir, recent_dir):
    for item_id in missed_id:
        srcpath = recent_dir+'/'+item_id+'.xpi'
        despath = missed_dir+'/'+item_id+'.xpi'
        try:
            shutil.move(srcpath, despath)
            print("handle_missed_file: success move:",item_id,file=open('firefox_log.txt','a'))
        except:
            print("handle_missed_file: no file ",item_id,file=open('firefox_log.txt','a'))


def find_new_add(new_file, old_file):
    return find_missed(old_file, new_file)


def download_new_add_ext(new_add_item, current_dir):
    num=0
    suc=0
    for item in new_add_item:
        # download the extension from chrom web store
        link = item['download_link']
        id=item['id']
        try:
            result = _DownloadCrxFromCws(id, link,current_dir)
            if result == False:
                num=num+1
                print('Empty file total: ',num)
            else:
                suc=suc+1
        except Exception as e:
            print('download failed:',id,'Exception:',e)
            print('download failed:',id, file=open("./firefox_log.txt", "a"))
    print("download successful total number:",suc, file=open("./firefox_log.txt","a"))
    print('Empty file total number: ',num, file=open("./firefox_log.txt", "a"))


def _DownloadCrxFromCws(ext_id, link,dst):
    """Downloads CRX specified from Chrome Web Store.
    Retrieves CRX (Chrome extension file) specified by ext_id from Chrome Web
    Store, into directory specified by dst.
    Args:
        ext_id: id of extension to retrieve.
        dst: directory to download CRX into
    Returns:
        Returns local path to downloaded CRX.
        If download fails, return None.
    """
    dst_path = os.path.join(dst, '%s.xpi' % ext_id)
    headers={
        'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',

    }
    req0 = urllib.request.Request(url=link,headers=headers)
    req = urllib.request.urlopen(url=req0,timeout=10)
    res = req.read()
    if req.getcode() != 200:
        print('download failed: ',ext_id,'the code:',req.getcode())
        print('download failed: ',ext_id, file=open("./firefox_log.txt", "a"))
        return False
#   print(res)
    with open(dst_path, 'wb') as f:
        f.write(res)
    print('download successful: ', ext_id)
    # print('download successful: ', ext_id, file=open("./log.txt","a"))
    return True


def delta_time(deltadays):
    current_date = datetime.date.today()
    past_list = []
    for i in range(deltadays):
        tmp = i+1
        past_time = current_date-datetime.timedelta(days=tmp)
        past_list.append(past_time)
    return past_list

# get recent released App list


def recent_release(new_file, delta):
    past_list = delta_time(delta)
    new_released = []
    with open(new_file) as json_file:
        new_list = json.load(json_file)
    for item in new_list:
        i_time = dparser.parse(item["last_updated"], fuzzy=True)
        i_date = datetime.date(i_time.year, i_time.month, i_time.day)
        if i_date in past_list:
            # new released
            new_released.append(item)
    return new_released


def recent_all_release(new_file):
    with open(new_file) as json_file:
        new_list = json.load(json_file)
    return new_list

# update recent_release.json

'''
def write_list_to_file(recent_list, recent_release_file):
    with open(recent_release_file, "w") as json_file:
        json.dump(recent_list, json_file)

# download new file to the folder '/recent'

def download_file_from_list(recent_list, recent_dir):
    empty_file_path = './malicious_ext_crawler/data/empty_file.json'
    old_file_list = os.listdir(recent_dir)
    recent_filename_list = []
    for i in recent_list:
        id = i["id"]
        download_link=i['download_link']
        filename = id+'.xpi'
        recent_filename_list.append(filename)
        if filename not in old_file_list:
            result = _DownloadCrxFromCws(id, download_link,recent_dir)
            if result == False:
                # download fail, add the extension to empty.json
                tmp_list = []
                if 0 != os.path.getsize(empty_file_path):
                    with open(empty_file_path, "r") as json_file:
                        tmp_list = json.load(json_file)
                tmp_list.append(i)
                with open(empty_file_path, "w") as json_file:
                    json.dump(tmp_list, json_file)

'''
def missed_all_app(new_file, count):

    missed_file = './malicious_ext_crawler/data/missed.json'
    missed_dir = './malicious_ext_crawler/data/missed'
    current_dir = './malicious_ext_crawler/data/current'
    scan_dir='./malicious_ext_crawler/data/scan'

    last_file=''
    if(count != 0):
        num=count-1
        last_file = './malicious_ext_crawler/data/firefox_ext_data_[%s]FILTER_KEYWORDS.json' % num
        [missed_item, missed_id] = find_missed(new_file, last_file)
        handle_missed_list(missed_item, missed_file)
        handle_missed_file(missed_id, missed_dir, current_dir)
        # print(missed_id)
        [new_add_item, new_add_id] = find_new_add(new_file, last_file)
    else:
        new_add_item = recent_all_release(new_file)
    download_new_add_ext(new_add_item, scan_dir)

# missed_all_app('./malicious_ext_crawler/data/firefox_ext_data_[3]FILTER_KEYWORDS.json',3)