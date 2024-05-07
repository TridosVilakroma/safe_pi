import logging,json,sys
from datetime import datetime,timedelta

logger=logging.getLogger('logger')


#################### get data ####################

def load_schedule(*args):
    try:
        with open('logs/configurations/scheduled_services.json','r') as f:
            return json.load(f)
    except Exception as e:
        logger.exception(e)
        print(Exception)
        print('e: ',e)

def sort_by_due(data,*args):
    categories={
        "ignore"   :   {},  #level 0
        "11_50"    :   {},  #level 1
        "0_10"     :   {},  #level 2
        "0"        :   {}}  #level 3

    for k,v in data.items():
        if not v['service_date']:
            categories['0'][k]=v
            continue
        sd=datetime.fromisoformat(v['service_date'])
        ci=timedelta(int(v['current_interval']))
        due_date=sd+ci
        ct=datetime.now()
        remaining_time=due_date.replace(microsecond=0)-ct.replace(microsecond=0)
        if remaining_time.days<=0:
            remaining_time=timedelta()
        if remaining_time>ci/2:
            categories['ignore'][k]=data[k]
            continue
        elif remaining_time>ci/10:
            categories['11_50'][k]=data[k]
            continue
        elif remaining_time>timedelta():
            categories['0_10'][k]=data[k]
            continue
        else:
            categories['0'][k]=data[k]
            continue
    return categories


#################### message center ####################

def format_message(data:dict,level:int,uuid:str,*args):
    msg={
        "name"     :  data['title'],
        "title"    :  '',
        "body"     :  '',
        "card"     :  data['title'],
        "gravity"  :  '',
        "lifetime" :  "5",
        "uuid"     :  uuid,
        "seen"     :  False
    }
    if level == 1:
        msg['gravity']=1
        msg['title']='Service Upcoming'
        msg['body']=f"{data['title']} has an upcoming service date."
    elif level == 2:
        msg['gravity']=5
        msg['title']='Service Upcoming'
        msg['body']=f"{data['title']} has an upcoming service date."
    elif level == 3:
        msg['gravity']=10
        msg['title']='Service Due'
        msg['body']=f"{data['title']} is currently due for service."
    return msg

def save_message(msg,*args):
    with open('logs/configurations/pushed_messages.json','r+') as data_base:
        data=json.load(data_base)
        if msg['uuid'] in data:
            return
        msg['timestamp']=str(datetime.now())
        data[msg['uuid']]=msg
        data_base.seek(0)
        json.dump(data, data_base, indent=4, skipkeys=True)
        data_base.truncate()

def remove_message(uuid,*args):
    with open('logs/configurations/pushed_messages.json','r+') as data_base:
        data=json.load(data_base)
        del data[uuid]
        data_base.seek(0)
        json.dump(data, data_base, indent=4, skipkeys=True)
        data_base.truncate()

#################### notificatons ####################

def add_icon_badge(data,*args):
    pass

def remove_icon_badge(data,*args):
    pass

def add_toast(data,*args):
    pass

def remove_toast(data,*args):
    pass

#################### updater ####################

def update(*args):
    data=sort_by_due(load_schedule())
    for k,i in data['11_50'].items():
        msg=format_message(data['11_50'][k],1,k)
        save_message(msg)
    for k,i in data['0_10']:
        msg=format_message(data['0_10'][k],2,k)
        save_message(msg)
    for k,i in data['0']:
        msg=format_message(data['0'][k],3,k)
        save_message(msg)
