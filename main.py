import music_cloud_api as api
import requests
import json
import pickle
import os
import time
import threading
import datetime
import sys
import random
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from collections import Counter

URL_PLAYLIST = 'http://music.163.com/weapi/v3/playlist/detail?csrf_token='
URL_USER='http://music.163.com/api/user/playlist/?offset=0&limit=0&uid='

def post(session, url, req, sec_pair):
    sec,enc_sec=sec_pair
    r=api.encrypted_request(req,sec,enc_sec)
    return session.post(url,data="params={params}&encSecKey={encSecKey}".format(**r)).text        
    
def get_playlist(session, id, sec):
    try:
        j=json.loads(post(session, URL_PLAYLIST,{"id": id,"limit": 0}, sec))
    except requests.exceptions.RequestException as re:
        raise Exception("failed to fetch playlist %d"%id)
    if j["code"]==404:
        #playlist does not exist
        assert False
        return []
    return [item['id'] for item in j["playlist"]["trackIds"]]

def get_user(session, id):
    try:
        j=json.loads(session.get(URL_USER+str(id)).text)
    except requests.exceptions.RequestException as re:
        raise Exception("failed to fetch user %d"%id)
            
    if len(j["playlist"])==0: return 0 #user does not exist
    
    return int(j["playlist"][0]["id"])

def save(data_name, content):
    open(data_name,"wb").write(pickle.dumps(content))

def load(data_name):
    return pickle.loads(open(data_name,"rb").read())
    
class FetchThread (threading.Thread):
    def __init__(self, proxy, secret_keys, task_pool):
        threading.Thread.__init__(self)
        self.task_pool = task_pool
        self.data=Counter()
        self.valid_uids = []
        self.task_num=0
        self.session=requests.Session()
        if proxy!=None: self.session.proxies.update(proxy)
        self.session.headers.update({'Content-Type': 'application/x-www-form-urlencoded'})
        self.session.mount('http://', HTTPAdapter(max_retries=Retry(total=5,backoff_factor=0.5)))
        self.secret_keys=secret_keys
        
        self.dg=datetime.timedelta()
        self.dm=datetime.timedelta()

    def run(self):
        while True:
            if VERBOSE: print(self,": remaining tasks count: ",len(task_pool))
            try:
                # try to get a task, notice that it is a multithreading environment
                task_id=self.task_pool.pop()
            except IndexError:
                break # no task was left
            try:
                tmp_data=Counter()
                tmp_uids=[]
                for user_id in range(task_id, task_id+TASK_LENGTH):
                    playlist_id=get_user(self.session, user_id)
                    if playlist_id==0: continue
                    tmp_uids.append(user_id)
                    sec=secret_keys[random.randint(0,len(secret_keys)-1)]
                    music_ids=get_playlist(self.session, playlist_id, sec)
                    for id in music_ids: tmp_data[id]+=1
                # merge data
                self.data+=tmp_data
                self.valid_uids.extend(tmp_uids)
                self.task_num+=1
            except Exception as e:
                if VERBOSE: print(thread, ": failed to fetch! [%d...%d]"%(task_id, task_id+TASK_LENGTH),e)
                print("oops...",e)
                self.task_pool.append(task_id)
    def get_num(self):
        return self.task_num
    def get_results(self):
        return (self.data,self.valid_uids)
        
def getProxy(num):
    num-=1 # One do not use proxy
    proxies=json.loads(requests.get("http://127.0.0.1:8000/?count="+str(num)+"&country=%E5%9B%BD%E5%86%85&protocol=1").text)
    if VERBOSE: print(proxies)
    fix=0
    if len(proxies)<num:
        print("[Warning] Not enough proxy IPs! We only have %d proxies."%len(proxies))
        fix=num-len(proxies)
    return [None]*(fix+1)+[{'https':p[0]+":"+str(p[1])} for p in proxies]

data_name="data"
buffer_valid = os.path.exists(data_name)
result,user_id,valid_uids=[Counter(),0,[]] if not buffer_valid else load(data_name)
MAX_USER_ID=460000000

THREAD_NUM=50
TASK_LENGTH=100
TASK_NUM=500
PROGRESS_BAR_LENGTH=60
threads=[]

OPTIONS=sys.argv[1:]
VERBOSE="--verbose" in OPTIONS
NO_PROXY=not "--proxy" in OPTIONS
if NO_PROXY:
    proxies=[None for p in range(THREAD_NUM)]
else:
    proxies=getProxy(THREAD_NUM)

task_pool=[]
if os.path.exists("keys"):
    secret_keys=load("keys")
else:
    print("Generating secret keys...")
    secret_keys=[api.generate_secpair() for i in range(THREAD_NUM*10)]
    save("keys",secret_keys)
print("Start...")
while user_id < MAX_USER_ID:
    print("Valid user number: {}. Valid music data: {}. Progress: {}/{}({:.5%})".format(len(valid_uids),len(result),user_id,MAX_USER_ID,user_id/MAX_USER_ID))
    # Assign tasks
    for i in range(TASK_NUM):
        task_pool.append(user_id)
        user_id+=TASK_LENGTH
    
    start_time=datetime.datetime.now()
    
    # Start threads
    for i in range(THREAD_NUM):
        thread=FetchThread(proxies[i], secret_keys, task_pool)
        thread.start()
        threads.append(thread)
        #print("thread created...", thread)
    
    while len(task_pool)>0:
        now_num=int((1-len(task_pool)/TASK_NUM)*PROGRESS_BAR_LENGTH)
        print("\r"+">"*now_num+"="*(PROGRESS_BAR_LENGTH-now_num)+" {}/{}({:.1%})".format(TASK_NUM-len(task_pool),TASK_NUM,1-len(task_pool)/TASK_NUM),end="")
        time.sleep(1)
    print("\r"+">"*PROGRESS_BAR_LENGTH+" {}/{}({:.1%})".format(TASK_NUM,TASK_NUM,1),end="")
    # Wait for threads
    mer=datetime.timedelta()
    for thread in threads:
        thread.join()
        if VERBOSE: print("thread closed:", thread, thread.get_num())
        data,uids=thread.get_results()
        st=datetime.datetime.now()
        result+=data
        valid_uids.extend(uids)
        mer+=datetime.datetime.now()-st
    print("mer",mer)    
    threads=[]
    
    # Save data
    save(data_name,[result,user_id,valid_uids])
    print(" {}...Saved. Speed: {:.5} user(s)/s\n".format(user_id,(TASK_LENGTH*THREAD_NUM)/(datetime.datetime.now()-start_time).seconds))
    
    