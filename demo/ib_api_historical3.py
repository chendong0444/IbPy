#!/usr/bin/env python
# coding=utf-8

from time import sleep, strftime, localtime
from ib.ext.Contract import Contract
from ib.ext.Order import Order
from ib.opt import ibConnection, message


gLock = True     # to know if downloading
new_symbolinput = ['GOOG', 'TWTR','CTRP','AAPL','AMZN','FB','JD']
newDataList = []
buy_symbols = []
sell_symbols =[]

def strategy(dataList):
    upPercet=0.0
    upCount=0
    downCount=0
    for msg in dataList:
        upP=(msg.close-msg.open)/msg.open * 100
        upPercet=upPercet+upP
        if upP>0:
            upCount=upCount+1
        elif upP<0:
            downCount=downCount+1
        else:
            pass
        print(upPercet,upP,upCount,downCount)
    
    # 如果5天内有2，3天涨，上涨10%，就卖
    if(upPercet>=10 and upCount>=2):
        sell_symbols.append(new_symbolinput[msg.reqId])
        print('sell : %s' % new_symbolinput[msg.reqId])
    # 如果5天内有2，3天跌，下跌15%，就买
    if(upPercet<= -15 and downCount>=2):
        buy_symbols.append(new_symbolinput[msg.reqId])
        print('buy : %s' % new_symbolinput[msg.reqId])
    

def create_order(action):
    order = Order()
    order.m_orderType = 'MKT'
    order.m_totalQuantity = 100
    order.m_action = action
    return order

def  create_contract(symbol):
    contract = Contract()
    contract.m_symbol = symbol
    contract.m_secType = 'STK'
    contract.m_exchange = 'SMART'
    contract.m_currency = 'USD'
    return contract


def historical_data_handler(msg):
    global newDataList
    if ('finished' in str(msg.date)) == False:
        newDataList.append(msg)


def error_handler(msg):
    print(msg)


def main():
    con = ibConnection()
    con.register(historical_data_handler, message.historicalData)
    con.register(error_handler, 'Error')
    con.connect()

    fr = open('symbols.csv','r')
    symbols=fr.readlines()[0].split(',')
    fr.close()
    global new_symbolinput
    new_symbolinput=symbols  #['ATEC'] 

    tickId = 10
    for symbol in new_symbolinput:
        qqq=create_contract(symbol)
        con.reqHistoricalData(tickId, qqq, '', '1 W', '1 day', 'TRADES', 1, 2)
        sleep(2)

        global newDataList
        if(len(newDataList)>=5):
            strategy(newDataList[0:5])
            newDataList=newDataList[5:]

            if len(buy_symbols)>0:
                c=create_contract(buy_symbols.pop())
                o=create_order('BUY')
                con.placeOrder(tickId, c, o)
                
            if len(sell_symbols)>0:
                c=create_contract(sell_symbols.pop())
                o=create_order('SELL')
                con.placeOrder(tickId,c,o)
                

        tickId = tickId + 1


if __name__ == '__main__':
    main()
    


