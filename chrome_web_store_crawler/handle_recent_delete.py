import time
import datetime

import json

import dateutil.parser as dparser

import os
import shutil
import urllib.request
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# find missed App
# exists in old_file, not in new_file
# return item list and id list


def find_missed(new_file, old_file):
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

    for item in missed_item:
        item["missed_date"]=current_time.strftime("%Y-%m-%d %H:%M:%S")

    if os.path.exists(missed_file):
        with open(missed_file,'r') as json_file:
            missed_list = json.load(json_file)
        for i in missed_item:
            missed_list.append(i)
    else:
        missed_list = missed_item

    with open(missed_file, "w") as json_file:
        json.dump(missed_list, json_file)

# move missed App source code from '/recent' to 'missed'


def handle_missed_file(missed_id, missed_dir, recent_dir):
    for item_id in missed_id:
        srcpath = recent_dir+'/'+item_id+'.crx'
        despath = missed_dir+'/'+item_id+'.crx'
        try:
            shutil.move(srcpath, despath)
            print("handle_missed_file: success move:",item_id,file=open('chrome_log.txt','a'))
        except:
            print("handle_missed_file: no file in missed directory")


def find_new_add(new_file, old_file):
    return find_missed(old_file, new_file)


def download_new_add_ext(new_add_item, current_dir):
    num=0
    suc=0
    for item in new_add_item:
        # download the extension from chrom web store
        id = item['id']
        try:
            result = _DownloadCrxFromCws(id, current_dir)
            if result == False:
                num=num+1
                print('Empty file total: ',num)
            else:
                suc=suc+1
        except:
            print('download failed:',id)
            print('download failed:',id, file=open("./chrome_log.txt", "a"))
    print("download successful total number:",suc, file=open("./chrome_log.txt","a"))
    print('Empty file total number: ',num, file=open("./chrome_log.txt", "a"))



def _DownloadCrxFromCws(ext_id, dst):
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
    dst_path = os.path.join(dst, '%s.crx' % ext_id)
    cws_url = ('https://clients2.google.com/service/update2/crx?response='
             'redirect&prodversion=38.0&x=id%%3D%s%%26installsource%%3D'
             'ondemand%%26uc' % ext_id)
    req = urllib.request.urlopen(cws_url)
    res = req.read()
    if req.getcode() != 200:
        print('download failed: ',ext_id)
        print('download failed: ',ext_id, file=open("./chrome_log.txt", "a"))
        return False
#   print(res)
    with open(dst_path, 'wb') as f:
        f.write(res)
    print('download successful: ', ext_id)
    # print('download successful: ', ext_id, file=open("./chrome_log.txt","a"))
    return True

# get the dalta date list
# input deltadays
# return date list


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

def missed_all_app(new_file, count):

    missed_file = './chrome_web_store_crawler/data/missed.json'
    missed_dir = './chrome_web_store_crawler/data/missed'
    current_dir = './chrome_web_store_crawler/data/current'
    scan_dir='./chrome_web_store_crawler/data/scan'

    last_file=''
    if(count != 0):
        num=count-1
        last_file = './chrome_web_store_crawler/data/full_list/chrome_ext_data_[%s]FILTER_KEYWORDS.json' % num
        [missed_item, missed_id] = find_missed(new_file, last_file)
        handle_missed_list(missed_item, missed_file)
        handle_missed_file(missed_id, missed_dir, current_dir)
        # print(missed_id)
        [new_add_item, new_add_id] = find_new_add(new_file, last_file)
    else:
        new_add_item = recent_all_release(new_file)
    download_new_add_ext(new_add_item, scan_dir)

if __name__ == "__main__":
    missed_all_app('./chrome_web_store_crawler/data/full_list/chrome_ext_data_[17]FILTER_KEYWORDS.json',17)