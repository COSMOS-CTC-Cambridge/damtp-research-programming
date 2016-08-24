
import threading, Queue, datetime, time
q=Queue.Queue()

def produce():
    myvar = 1
    while True:
        if (q.empty()):
            q.put(datetime.datetime.utcnow())
        else:
            time.sleep(1)
            mistake
    return

def consume():
    now = datetime.datetime.utcnow()
    while (datetime.datetime.utcnow() > now + datetime.timedelta(seconds=100)):
        if not(q.empty()):
            print(q.get())
    return

t=threading.Thread(target=produce)
t.start()
consume()
