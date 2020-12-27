import os
import time
import json
import requests
import csv

engine_list=["ALYac","APEX","AVG","Acronis","Ad-Aware","AegisLab","AhnLab-V3",
                    "Alibaba","Antiy-AVL","Arcabit","Avast","Avast-Mobile","Avira",
                    "Baidu","BitDefender","BitDefenderFalx","BitDefenderTheta","Bkav",
                    "CAT-QuickHeal","CMC","ClamAV","Comodo","CrowdStrike","Cybereason",
                    "Cylance","Cynet","Cyren","DrWeb","ESET-NOD32","Elastic","Emsisoft",
                    "F-Secure","FireEye","Fortinet","GData","Gridinsoft","Ikarus",
                    "Jiangmin","K7AntiVirus","K7GW","Kaspersky","Kingsoft","MAX",
                    "Malwarebytes","MaxSecure","McAfee","McAfee-GW-Edition","MicroWorld-eScan",
                    "Microsoft","NANO-Antivirus","Paloalto","Panda","Qihoo-360","Rising",
                    "SUPERAntiSpyware","Sangfor","SentinelOne","Sophos","Symantec",
                    "SymantecMobileInsight","TACHYON","Tencent","TotalDefense","Trapmine",
                    "TrendMicro","TrendMicro-HouseCall","Trustlook","VBA32","VIPRE",
                    "ViRobot","Webroot","Yandex","Zillya","ZoneAlarm","Zoner","eGambit"]
def scanByFilePath(file_path,file_id):
    apikey='787cef5ac6d5f3fdeacd068c97180caa26c89ff69aee1c2b012a2ace62e993b9'  
    myheaders={
        'x-apikey':apikey
    }
    scan_url='https://www.virustotal.com/api/v3/files'
    myfiles = {'file': (file_path, open(file_path, 'rb'))}
    analysis=requests.post(scan_url,headers=myheaders,files=myfiles)
            
    # print(analysis.text)
    analysis_json=json.loads(analysis.text)
    tmp={
        'name':file_id,
        'id':analysis_json["data"]["id"]
    }
    return tmp

def scanByDir():
    apikey='787cef5ac6d5f3fdeacd068c97180caa26c89ff69aee1c2b012a2ace62e993b9'  
    myheaders={
        'x-apikey':apikey
    }
    scan_url='https://www.virustotal.com/api/v3/files'

    file_folder='chrome_web_store_crawler/chrome_data_analysis/data/current/'
    file_list=os.listdir(file_folder)

    # store the analysis id
    output_file='chrome_web_store_crawler/chrome_data_analysis/data/scan_result_id.json'
    output_list=[]

    with open(output_file,'r') as f:
        output_list=json.load(f)

    for i in file_list:
        if i=='.DS_Store':
            continue
        file_path=file_folder+i
        
        print("scan file:",file_path)
        
    
        #scan the file and get the result
        myfiles = {'file': (file_path, open(file_path, 'rb'))}
        analysis=requests.post(scan_url,headers=myheaders,files=myfiles)
            
        # print(analysis.text)
        analysis_json=json.loads(analysis.text)
        [ext_name,ext]=os.path.splitext(i)
        tmp={
            'name':ext_name,
            'id':analysis_json["data"]["id"]
        }
        output_list.append(tmp)
        print(tmp["id"])
        
        # print("start to wait...")
        time.sleep(10)

    with open(output_file,'w') as f:
        json.dump(output_list,f)
    print("updated output_file")

def storeOriginResult(id,res):
    analysis_origin_file='chrome_web_store_crawler/chrome_data_analysis/data/analysis_result_origin.json'
    tmp_list = []
    if 0 != os.path.getsize(analysis_origin_file):
        with open(analysis_origin_file, "r") as json_file:
            tmp_list = json.load(json_file)   
    tmp_list.append(res)
    with open(analysis_origin_file, "w") as json_file:
        json.dump(tmp_list, json_file)

def handleOriginResult(id,res_json):
    result_file_csv='chrome_web_store_crawler/chrome_data_analysis/data/analysis_result.csv'
    engine_res= res_json["data"]["attributes"]["results"]
    vul_count=0
    # store the engine info where the result is not null
    res_list_csv=[id]
    mid_list_json=[]
    for engine in engine_list:
        try:
            res=engine_res[engine]["result"]
        except:
            res_list_csv.append('null')
            continue
        if res!=None:
            # the result is not null
            # add into result list
            vul_count=vul_count+1
            engine_res[engine]["name"]=engine
            mid_list_json.append(engine_res[engine])
            res_list_csv.append(res)
            print("in extension:",id,"find bug in:",engine,"output:",res)

        else:
            res_list_csv.append('null')
    tmp_json={
        'id':id,
        'result':mid_list_json
    }
    with open(result_file_csv,'a') as f:
        writer=csv.writer(f)
        writer.writerow(res_list_csv)
    if vul_count==0:
        print("no error in extension: ",id)

    return tmp_json

def getAnalysisResult():
    apikey='787cef5ac6d5f3fdeacd068c97180caa26c89ff69aee1c2b012a2ace62e993b9'  
    myheaders={
        'x-apikey':apikey
    }

    scan_id_file='chrome_web_store_crawler/chrome_data_analysis/data/scan_result_id.txt'
    output_file=[]
    with open(scan_id_file,'r') as f:
        output_file=f.readlines()

    print("start to get analysis result...")
    count=0
    for i in output_file:
        count=count+1
        if count<=150:
            continue
        theID=i.strip('\n')
        print("handle count",count,"id:",theID)
        res_url="https://www.virustotal.com/api/v3/analyses/%s" % theID
        result=requests.get(res_url,headers=myheaders)
        res_str=result.text
        null=''
        res_json=json.loads(res_str)

        # store the origin result
        storeOriginResult(theID,res_json)

        # break
        print("wait...")
        time.sleep(10)

getAnalysisResult()

# read the result from the origin file
origin_list=[]
origin_file='chrome_web_store_crawler/chrome_data_analysis/data/analysis_result_origin.json'
with open(origin_file,'r') as f:
    origin_list=json.load(f)

csv_header=["name"]+engine_list
result_file_csv='chrome_web_store_crawler/chrome_data_analysis/data/analysis_result.csv'
with open(result_file_csv,'w') as f:
    writer = csv.writer(f)
    writer.writerow(csv_header)

# the file stores handled analysis result
result_file='chrome_web_store_crawler/chrome_data_analysis/data/analysis_result.json'
handled_result=[]

for item in origin_list:
    
    item_json=item
    try:
        thePath=item_json["meta"]['file_info']['name']
        [thedir,thename]=os.path.split(thePath)
        [theID,theext]=os.path.splitext(thename)
    except:
        theID='**'
    tmp_json=handleOriginResult(theID,item_json)
    handled_result.append(tmp_json)

with open(result_file,'w') as f:
    json.dump(handled_result,f)

# res_str=res_str.replace('null','')
# scan_res=json.loads(res_str)
# null=''
# scan_res={
#     "data": {
#         "attributes": {
#             "date": 1607875360,
#             "results": {
#                 "ALYac": {
#                     "category": "undetected",
#                     "engine_name": "ALYac",
#                     "engine_update": "20201213",
#                     "engine_version": "1.1.1.5",
#                     "method": "blacklist",
#                     "result": "null"
#                 },
#             },
#             "stats": {
#                 "confirmed-timeout": 0,
#                 "failure": 0,
#                 "harmless": 0,
#                 "malicious": 0,
#                 "suspicious": 0,
#                 "timeout": 0,
#                 "type-unsupported": 16,
#                 "undetected": 60
#             },
#             "status": "completed"
#         },
#         "id": "MTk0NTc3YTdlMjBiZGNjN2FmYmI3MThmNTAyYzEzNGM6MTYwNzg3NTM2MA==",
#         "type": "analysis"
#     },
#     "meta": {
#         "file_info": {
#             "md5": "194577a7e20bdcc7afbb718f502c134c",
#             "name": "chrome_web_store_crawler/chrome_data_analysis/data/current/.DS_Store",
#             "sha1": "df2fbeb1400acda0909a32c1cf6bf492f1121e07",
#             "sha256": "d65165279105ca6773180500688df4bdc69a2c7b771752f0a46ef120b7fd8ec3",
#             "size": 6148
#         }
#     }
# }