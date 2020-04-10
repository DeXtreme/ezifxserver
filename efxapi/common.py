from datetime import datetime,timedelta
import pytz
import math

def is_market_open():
    time=datetime.now(pytz.timezone('US/Eastern'))
    print(time)
    if ((time.weekday()==6 and time.hour>=18) or (time.weekday() in [0,1,2,3]) or (time.weekday()==4 and time.hour<16)): #weekdays
        if((time.month==12 and time.date==24 and time.hour>=18) or (time.month==12 and time.date==25) or (time.month==12 and time.date==26 and time.hour<16)): #christmas
            return False
        elif ((time.month==12 and time.date==31 and time.hour>=18) or (time.month==1 and time.date==1) or (time.month==1 and time.date==2 and time.hour<16)): #new year
            return False
        else:
            return True    
    else:
        return False


def get_market_times(close_time=None,open_time=None):
    time=datetime.now(pytz.timezone('US/Eastern')) if open_time==None else open_time

    if ((time.month==12 and time.date==24 and time.hour>=18) or (time.month==12 and time.date==25) or (time.month==12 and time.date==26 and time.hour<16)):
        new_close=time.replace(hour=16,minute=0,second=0,day=24) if close_time==None else close_time
        new_open=time.replace(hour=18,minute=0,second=0,day=26)

        return get_market_times(new_close,new_open)
    elif ((time.month==12 and time.date==31 and time.hour>=18) or (time.month==1 and time.date==1) or (time.month==1 and time.date==2 and time.hour<16)): #new year
        
        new_close=time.replace(hour=16,minute=0,second=0,day=31,month=12) if close_time==None else close_time

        then=time=datetime.now(pytz.timezone('US/Eastern'))+timedelta(days=1)
        new_open=then.replace(hour=18,minute=0,second=0,day=2,month=1)

        return get_market_times(new_close,new_open)
    elif ((time.weekday()==6 and time.hour>=18) or (time.weekday() in [0,1,2,3]) or (time.weekday()==4 and time.hour<18)):
        if(open_time==None):
            if (time.hour>=18):
                time=time+timedelta(days=1)

            new_close=time.replace(hour=16,minute=0,second=0) if close_time==None else close_time
            new_open=time.replace(hour=18,minute=0,second=0)
            
            return get_market_times(new_close,new_open)
        else:
            return [close_time.astimezone(),open_time.astimezone()]
    elif ((time.weekday() in [4,5]) or (time.weekday()==6 and time.hour<18)):

        new_close=time.replace(hour=16,minute=0,second=0) + timedelta(days=4-time.weekday()) if close_time==None else close_time
        new_open=time.replace(hour=18,minute=0,second=0) + timedelta(days=6-time.weekday())

        return get_market_times(new_close,new_open)
        
    


    
        

def round_half_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(n*multiplier + 0.5) / multiplier

def round_half_down(n, decimals=0):
    multiplier = 10 ** decimals
    return math.ceil(n*multiplier - 0.5) / multiplier