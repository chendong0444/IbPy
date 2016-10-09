from time import sleep, strftime, localtime
from ib.ext.Contract import Contract
from ib.opt import ibConnection, message


gLock = False     # to know if downloading
new_symbolinput = ['GOOG', 'TWTR','CTRP','AAPL','AMZN','FB','JD']
newDataList = []

def strategy(dataList):
    upPercet=0.0
    upCount=0
    downCount=0
    for msg in dataList:
        upP=(msg.close-msg.open)/msg.open * 100
        upPercet=upPercet+upP
        # print(upPercet,upP,upCount,downCount)
        if upP>0:
            upCount=upCount+1
            # print(upP,upCount)
        elif upP<0:
            downCount=downCount+1
            # print(upP,downCount)
        else:
            pass
        print(upPercet,upP,upCount,downCount)
        pass
    
    if(upPercet>=10 and upCount>=2) or (upPercet<= -15 and downCount>=2):
        return msg.reqId

    return -1


def historical_data_handler(msg):
    global newDataList
    global gLock
    gLock = False
    # print (msg)
    if ('finished' in str(msg.date)) == False:
        new_symbol = new_symbolinput[msg.reqId]
        dataStr = '%s, %s, %s, %s' % (new_symbol, msg.date,msg.open, msg.close)
        print(dataStr)
        # newDataList = newDataList + [dataStr]
        newDataList.append(msg)
        # print(newDataList)
    else:
        pass

def watchAll_handler(msg):
    print(msg)


con = ibConnection()
con.register(historical_data_handler, message.historicalData)
con.registerAll(watchAll_handler)
con.connect()

symbol_id = 0
gLock = True


fr = open('symbols.csv','r')
symbols=fr.readlines()[0].split(',')
fr.close()
# print(symbols)
new_symbolinput=symbols  #['ATEC'] 
# print(new_symbolinput)

for symbol in new_symbolinput:
    # print(symbol)
    if(len(symbol)>4):
	    continue

    qqq = Contract()
    qqq.m_symbol = symbol
    qqq.m_secType = 'STK'
    qqq.m_exchange = 'SMART'
    qqq.m_currency = 'USD'

    gLock=True

    con.reqHistoricalData(symbol_id, qqq, '', '1 W', '1 day', 'TRADES', 1, 2)

    symbol_id = symbol_id + 1

    
    while gLock is True:
        sleep(2)

        if(len(newDataList)>=5):
            # print("1")
            reqId=strategy(newDataList[0:5])
            print(reqId)
            if(reqId>-1):
                print('/********  %s matched strategy  *******/' % new_symbolinput[reqId])
                with open('result.txt','a',0) as fw:
                    fw.write(new_symbolinput[reqId]+',')
                
            newDataList=newDataList[5:]
        else:
            print("0")
    




