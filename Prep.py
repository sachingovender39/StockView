import pandas as pd
import pytz as tz
from datetime import datetime


def getlocalindex(index,meta):   
    local_index=[]
    format = '%Y-%m-%d %H:%M:%S'
    old_timezone = tz.timezone(meta['6. Time Zone'])
    new_timezone = tz.timezone("Africa/Johannesburg")
    for i in index:
        actual_datetime=datetime.strptime(str(i), format)
        local_timestamp = old_timezone.localize(actual_datetime).astimezone(new_timezone) 
        #local_index.append(local_timestamp.strftime(format))
        local_index.append(local_timestamp)
    return local_index

def prepTS(data,meta):
    data.index = getlocalindex(data.index,meta)
    data.columns=['Open','High','Low','Close','Volume']
    data = data.iloc[::-1]
    data=data.tz_localize(None)
    return data

def prepInd(data,meta):
    data.index = getlocalindex(data.index,meta)
    data=data.tz_localize(None)
    return data 

def getSMA(data,samples):
    close = data[['Close']].copy()
    close['SMA'] = close.rolling(samples).mean()
    return close

