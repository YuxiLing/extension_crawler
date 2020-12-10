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
    missed_list = []
    if 0 != os.path.getsize(missed_file):
        with open(missed_file) as json_file:
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
            print('download failed:',id, file=open("./log.txt", "a"))
    print("download successful total number:",suc, file=open("./log.txt","a"))
    


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
        print('download failed: ',ext_id, file=open("./log.txt", "a"))
        return False
#   print(res)
    with open(dst_path, 'wb') as f:
        f.write(res)
    print('download successful: ', ext_id)
    # print('download successful: ', ext_id, file=open("./log.txt","a"))
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

# update recent_release.json


def update_recent_list(recent_list, recent_release_file):
    with open(recent_release_file, "w") as json_file:
        json.dump(recent_list, json_file)

# download new file to the folder '/recent'


def update_recent_file(recent_list, recent_dir):
    empty_file_path = './chrome_web_store_crawler/chrome_data_analysis/tmpdata/empty_file.json'
    old_file_list = os.listdir(recent_dir)
    recent_filename_list = []
    for i in recent_list:
        id = i["id"]
        filename = id+'.crx'
        recent_filename_list.append(filename)
        if filename not in old_file_list:
            # need to download by id
            result = _DownloadCrxFromCws(id, recent_dir)
            if result == False:
                # download fail, add the extension to empty.json
                tmp_list = []
                if 0 != os.path.getsize(empty_file_path):
                    with open(empty_file_path, "r") as json_file:
                        tmp_list = json.load(json_file)
                tmp_list.append(i)
                with open(empty_file_path, "w") as json_file:
                    json.dump(tmp_list, json_file)


def missed_potential_app(new_file, count):
    recent_file = './chrome_web_store_crawler/chrome_data_analysis/tmpdata/recent_release.json'
    missed_file = 'chrome_web_store_crawler/chrome_web_store_crawler/chrome_data_analysis/tmpdata/missed.json'
    missed_dir = 'chrome_web_store_crawler/chrome_web_store_crawler/chrome_data_analysis/tmpdata/missed'
    recent_dir = 'chrome_web_store_crawler/chrome_web_store_crawler/chrome_data_analysis/tmpdata/recent'
    recent_release_file = './chrome_web_store_crawler/chrome_data_analysis/tmpdata/recent_release.json'
    if count != 0:
        [missed_item, missed_id] = find_missed(new_file, recent_file)
        handle_missed_list(missed_item, missed_file)
        handle_missed_file(missed_id, missed_dir, recent_dir)
        print(missed_id)
    else:
        try:
            os.mkdir(
                './chrome_web_store_crawler/chrome_data_analysis/tmpdata/recent')
        except Exception as e:
            print("the recent directory has existed ", e)
        try:
            os.mkdir(
                './chrome_web_store_crawler/chrome_data_analysis/tmpdata/missed')
        except Exception as e:
            print("the missed directory has existed ", e)
    recent_list = recent_release(new_file, 20)
    print(recent_list)
    update_recent_list(recent_list, recent_release_file)
    update_recent_file(recent_list, recent_dir)

# new_file: 'chrome_web_store_crawler/chrome_data_analysis/tmpdata/chrome_ext_data_[%s]FILTER_KEYWORDS.json'


def missed_all_app(new_file, count):
    try:
        os.mkdir('./chrome_web_store_crawler/chrome_data_analysis/data/current')
    except Exception as e:
        print("the current directory has existed ", e)
    try:
        os.mkdir('./chrome_web_store_crawler/chrome_data_analysis/data/missed')
    except Exception as e:
        print("the missed directory has existed ", e)

    missed_file = './chrome_web_store_crawler/chrome_data_analysis/data/missed.json'
    missed_dir = './chrome_web_store_crawler/chrome_data_analysis/data/missed'
    current_dir = './chrome_web_store_crawler/chrome_data_analysis/data/current'

    # last_file = './chrome_web_store_crawler/chrome_data_analysis/data/last.json'
    last_file=''
    if(count != 0):
        last_file = './chrome_web_store_crawler/chrome_data_analysis/tmpdata/chrome_ext_data_[%s]FILTER_KEYWORDS.json' % count-1
        [missed_item, missed_id] = find_missed(new_file, last_file)
        handle_missed_list(missed_item, missed_file)
        handle_missed_file(missed_id, missed_dir, current_dir)
        # print(missed_id)
        [new_add_item, new_add_id] = find_new_add(new_file, last_file)
    else:
        new_add_item = recent_all_release(new_file)
    download_new_add_ext(new_add_item, current_dir)
