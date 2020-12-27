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

import get_code_find_missed
import scan_ext_file


######## Remove duplicates
# remove duplicates def
# Remove duplicates
def remove_dup_list_dic(test_list):
    res_list = [] 
    for i in range(len(test_list)): 
        if test_list[i] not in test_list[i + 1:]: 
            res_list.append(test_list[i])

    return res_list


# Export csv
# return csv and remove dups
def export_csv(filter_cleaned_data,csv_file):
   
    final_data = remove_dup_list_dic(filter_cleaned_data)
    
    # csv_columns = ['platform','key','name', 'rating', 'user_numbers', 'creator', 'last_updated', 'reviews']
    csv_columns = ['platform', 'id', 'download_link','key','name', 'rating', 'download_numbers', 'creator', 'last_updated', 'reviews']

    with open(csv_file, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in final_data:
            writer.writerow(data)

# return 8 latest month result and remove dups(from Jan to Aug)
def processing_latest_months(input_file):
    data = []
    months = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    with open(input_file) as json_file:
        data_dict = json.load(json_file)

        # Removing duplicates
        clean_data = remove_dup_list_dic(data_dict)
        
        for p in clean_data:
            # get all have last_updated in 2020
            date_type = dparser.parse(p["last_updated"],fuzzy=True)
            # 2020
            if (date_type.year == 2020):
                data.append(p)

    y_units = months

    result = [y_units, data]
    return result


################# CLEANER after run BOT- CRAWLER (using keywords)
# find substring without case sensitives
def f_wo_case(substring, main_string):

    if re.search(substring, main_string, re.IGNORECASE):
        return True

    return False
# This will filter the result from crawler one more time by using popular keywords
# para
def filter_keywords(input_file, output_file):
    cleaned_data = []
    # with open('combined.json') as json_file:
    #     data_dict = json.load(json_file)
    input_file = input_file + '.json'
    with open(input_file) as json_file:
        data_dict = json.load(json_file)

    

    for each in data_dict:

        # date_type = dparser.parse(each["last_updated"],fuzzy=True)
        ####### Using key filters
        key = each["key"]
        common_words_filters_key = (key.find("bit") != -1 or key.find("coin") != -1 or key.find("wallet") != -1 or key.find("exchange") != -1 or key.find("token") != -1 or \
                key.find("ether") != -1 or key.find("currency") != -1 or key.find("exchange") != -1 or key.find("crypto") != -1 or \
                key.find("chain") != -1 or key.find("cash") != -1 or key.find("transaction") != -1 or key.find("bank") != -1 or \
                key.find("pay") != -1 or key.find("money") != -1 or key.find("card") != -1 or key.find("card") != -1 or \
                key.find("binance") != -1 or key.find("ledger") != -1 or key.find("ledger") != -1 or key.find("trezor") != -1 or key.find("trezor") != -1 )

        filters_key = ( common_words_filters_key and (key.find("theme") == -1) )

        ######## Using name filters
        name = each["name"]     
        # Reason for excluding them because opera has a bac search engine that cannt effectively classify theme and extensions
        common_words_filters_name = (f_wo_case("bit", name) == True or f_wo_case("coin", name) == True or f_wo_case("wallet", name) == True or f_wo_case("exchange", name) == True or f_wo_case("token", name) == True or \
                f_wo_case("ether", name) == True or f_wo_case("currency", name) == True or f_wo_case("exchange", name) == True or f_wo_case("crypto", name) == True or \
                f_wo_case("chain", name) == True or f_wo_case("cash", name) == True or f_wo_case("transaction", name) == True or f_wo_case("bank", name) == True or \
                f_wo_case("pay", name) == True or f_wo_case("money", name) == True or f_wo_case("card", name) == True or f_wo_case("bit", name) == True or \
                f_wo_case("nance", name) == True or f_wo_case("ledger", name) == True or f_wo_case("trezor", name) == True) 

        filters_name = ( common_words_filters_name and (f_wo_case("theme", name) == False) )
        
        ####### combining name and key filters by OR
        filters = filters_key or filters_name
        
        if (filters):
            cleaned_data.append(each)



    # with open('cleaned_data.json', 'w') as cleaned_json:
    # 	json.dump(cleaned_data, cleaned_json)
    # EXPORT JSON
    output_file = output_file + 'FILTER_KEYWORDS' + '.json'
    with open(output_file, 'w') as cleaned_json:
        json.dump(cleaned_data, cleaned_json)

   
    #### EXPORT CSV if need, uncomment
    # csv_columns = ['platform', 'id', 'key','name', 'rating', 'user_numbers', 'creator', 'last_updated']
    # csv_file = "chrome_cleaned_data.csv"

    # with open(csv_file, 'w') as csvfile:
    #     writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
    #     writer.writeheader()
    #     for data in cleaned_data:
    #         writer.writerow(data)





############################### RUN BOT
# import string
# def job(t):
#     print("I'm working...", t)
#     return

# schedule.every().day.at("15:35").do(job,'It is 01:00')
# count how many time have the bot completed 
completed_count = 1

while True:
    # schedule.run_pending()
    # print("I'm working...",datetime.datetime.now())
    # time.sleep(5) # wait one minute
    # printing time and bot to log file
    print("+++++++++++++++++++++++++++++++++++++++++++++++++", file=open("opera_log.txt", "a"))
    # for i in range(8):
    #     time.sleep(3600)
    #     print("Slept one hour, now is ",datetime.datetime.now(),file=open("opera_log.txt","a"))

    print("Started program at", datetime.datetime.now(), file=open("opera_log.txt", "a"))
    print("And completed_count=", completed_count, file=open("opera_log.txt", "a"))

    print("*Bot is working....", file=open("opera_log.txt", "a"))
    # a = '-time' + 'aaaa'

    # name_exported_file = '-time_is[%s]' % datetime.datetime.now().strftime('%Y_%m_%d_%H:%M')
    # name after chrome_ext_data.........
    name_exported_file = './malicious_ext_crawler/data/full_list/opera_ext_data_[%s].json' % completed_count
    ######RUN-BOT
    # run scrapy through command liness
    # print to std out the result for debugging comment this if you want.
    result = subprocess.run(['scrapy', 'crawl', 'opera_extensions_meta', '-o', name_exported_file ], stdout=subprocess.PIPE)
 
    # after run bot run filter using keywords
    print("*Bot finished....", file=open("opera_log.txt", "a"))


    ######POST-PROCESSING
    print("Increased completed_count", file=open("opera_log.txt", "a"))
    name_exported_file_1 = '_[%s]' % completed_count

    print("Run FILTER using keywords....", file=open("opera_log.txt", "a"))
    # this variable includes url and name of the corresponding exported file from the bot each time
    name_exported_file_after_running_bot = './malicious_ext_crawler/data/full_list/opera_ext_data' + name_exported_file_1
    filter_keywords(name_exported_file_after_running_bot, name_exported_file_after_running_bot)
    
    
    
    print("FILTER using keywords finished", file=open("opera_log.txt", "a"))
    print("Run 8 latest months filter", file=open("opera_log.txt", "a"))
    print("Running latest months filter....", file=open("opera_log.txt", "a"))
    # name of the result after filtering using keywords
    name_exported_file_after_running_bot_csv = name_exported_file_after_running_bot + 'FILTER_KEYWORDS' + '.json'
    # get 2020 onlys
    y_1 = processing_latest_months(name_exported_file_after_running_bot_csv)
    print("Finished 8 latest months filter", file=open("opera_log.txt", "a"))
    print("Exporting csvvvvvv....", file=open("opera_log.txt", "a"))
    # get data and export to csv
    export_csv(y_1[1],name_exported_file_after_running_bot + 'FILTER_YEAR' + '.csv')
    print("Exporting csvvvvvv is finished....", file=open("opera_log.txt", "a"))

    # get source code and find missed extensions
    print("Getting source code and finding missed extensions....", file=open("opera_log.txt", "a"))
    get_code_find_missed.missed_all_app(name_exported_file_after_running_bot_csv,completed_count)

    print("Scanning new added source code...", file=open("opera_log.txt", "a"))
    scan_ext_file.startScan(completed_count)
    
    # increase the count to name the output file
    completed_count = completed_count + 1

    print("Finished the WHOLE process at", datetime.datetime.now(), file=open("opera_log.txt", "a"))
    print("Started to wait 8 hours at", datetime.datetime.now(), file=open("opera_log.txt", "a"))
    # time.sleep(28800) #sleep for 8 hour then repeat
    for i in range(8):
        time.sleep(3600)
        print("Slept one hour, now is ",datetime.datetime.now(),file=open("opera_log.txt","a"))
    # print a newline between each time after running bot.
    print("+++++++++++++++++++++++++++++++++++++++++++++++++\n", file=open("opera_log.txt", "a"))

