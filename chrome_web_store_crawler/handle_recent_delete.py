import schedule
import time
import datetime  
import subprocess


import json
# from datetime import datetime
import dateutil.parser as dparser
import matplotlib.pyplot as plt
import re
import csv
import os
import shutil

# find missed App 
# exists in old_file, not in new_file
# return item list and id list
def find_missed(new_file,old_file):
    new_list=[]
    old_list=[]
    missed_item=[]
    missed_id=[]
    with open(new_file) as json_file:
        new_list=json.load(json_file)
    with open(old_file) as json_file:
        old_list=json.load(json_file)
    for item in old_list:
        item_id=item["id"]
        isMissed=True
        for new_item in new_list:
            if new_item["id"]==item_id:
                isMissed=False
                break
        if isMissed:
            missed_item.append(item)
            missed_id.append(item_id)
    return [missed_item,missed_id]

# store missed App list in '/missed.json'
def handle_missed_list(missed_item):
    missed_file='chrome_web_store_crawler/chrome_web_store_crawler/chrome_data_analysis/tmpdata/missed.json'
    missed_list=[]
    if 0!=os.path.getsize(missed_file):
        with open(missed_file) as json_file:
            missed_list=json.load(json_file)
        for i in missed_item:
            missed_list.append(i)
    
    else:
        missed_list=missed_item

    with open(missed_file,"w") as json_file:
        json.dump(missed_list,json_file)

# move missed App source code from '/recent' to 'missed'
def handle_missed_file(missed_id):
    missed_dir='chrome_web_store_crawler/chrome_web_store_crawler/chrome_data_analysis/tmpdata/missed'
    recent_dir='chrome_web_store_crawler/chrome_web_store_crawler/chrome_data_analysis/tmpdata/recent'
    for item in missed_id:
        srcpath=recent_dir+'/'+item+'.crx'
        despath=missed_dir+'/'+item+'.crx'
        shutil.move(srcpath,despath)

# get the dalta date list
# input deltadays
# return date list
def delta_time(deltadays):
    current_date=datetime.date.today()
    past_list=[]
    for i in range(deltadays):
        tmp=i+1
        past_time=current_date-datetime.timedelta(days=tmp)
        past_list.append(past_time)
    return past_list

# get recent released App list
def recent_release(new_file,delta):
    past_list=delta_time(delta)
    new_released=[]
    with open(new_file) as json_file:
        new_list=json.load(json_file)
    for item in new_list:
        i_time = dparser.parse(item["last_updated"],fuzzy=True)
        i_date=datetime.date(i_time.year,i_time.month,i_time.day)
        if i_date in past_list:
            # new released
            new_released.append(item)
    return new_released

# update recent_release.json 
def update_recent_list(recent_list):
    list_path='chrome_web_store_crawler/chrome_web_store_crawler/chrome_data_analysis/tmpdata/recent_release1.json'
    with open(list_path,"w") as json_file:
        json.dump(recent_list,json_file)

# download new file to the folder '/recent'
def update_recent_file(recent_list):
    recent_file_path='chrome_web_store_crawler/chrome_web_store_crawler/chrome_data_analysis/tmpdata/recent'
    old_file_list=os.listdir(recent_file_path)
    recent_filename_list=[]
    for i in recent_list:
        id=i["id"]
        filename=id+'.crx'
        recent_filename_list.append(filename)
        if filename not in old_file_list:
            # need to download by id
            print("douwnload a new file")
    
    # remove useless file
    for i in old_file_list:
        if i not in recent_filename_list:
            # remove
            # os.remove(recent_file_path+'/'+i)
            print("remove",i)


def missed_potential_app(new_file,count):
    recent_file='chrome_web_store_crawler/chrome_web_store_crawler/chrome_data_analysis/tmpdata/recent_release.json'
    if count!=0:
        [missed_item,missed_id]=find_missed(new_file,recent_file)
        handle_missed_list(missed_item)
        handle_missed_file(missed_id)
        print(missed_id)
    else:
        os.mkdir('chrome_web_store_crawler/chrome_web_store_crawler/chrome_data_analysis/tmpdata/recent')
        os.mkdir('chrome_web_store_crawler/chrome_web_store_crawler/chrome_data_analysis/tmpdata/missed')
    recent_list=recent_release(new_file,20)
    print(recent_list)
    update_recent_list(recent_list)
    update_recent_file(recent_list)

# old_file='/chrome_web_store_crawler/chrome_web_store_crawler/chrome_data_analysis/tmpdata/chrome_ext_data-time_[0].json'
# new_file='chrome_web_store_crawler/chrome_web_store_crawler/chrome_data_analysis/tmpdata/chrome_ext_data-time_[0]_new.json'
# recent_file='chrome_web_store_crawler/chrome_web_store_crawler/chrome_data_analysis/tmpdata/recent_release.json'

