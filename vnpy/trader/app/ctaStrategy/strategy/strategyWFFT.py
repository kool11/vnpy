# encoding: UTF-8

from __future__ import division

from vnpy.trader.vtObject import VtBarData
from vnpy.trader.vtConstant import EMPTY_STRING
from vnpy.trader.app.ctaStrategy.ctaTemplate import (CtaTemplate,
                                                     BarGenerator,
                                                   ArrayManager)
import WFFT


class WfftStrategy(CtaTemplate):
    className = 'WfftStrategy'
    
    initDays = 10     

    N = 25
    len_ = 10
    q = 15
    Tq = 0.00002
    Length = 30
    Dq = 0.5

    BarsSinceEntry = -1
    MyEntryPrice = []
    HighestAfterEntry = []
    LowestAfterEntry = []

    TrailingStart = 72
    TrailingStop = 27
    MinPoint = 0.01
    StopLossSet = 37
    paramList = ['name',
                 'className',
                 'author',
                 'vtSymbol',
                 'N',
                 'len',
                 'q',
                 'Tq',
                 'Length',
                 'Dq',
                 'TrailingStart',
                 'TrailingStop',
                 'MinPoint',
                 'StopLossSet']

    varList = ['inited',
               'trading',
               'pos']

    syncList = ['pos']

    def __init__(self, ctaEngine, setting):
        super(WfftStrategy, self).__init__(ctaEngine, setting)

        self.bg = BarGenerator(self.onBar, 5)  
        self.am = ArrayManager()

        self.wfft = WFFT.pythonToCpp()
        self.wfft.setWfftSetting(self.N, self.len_, self.q, self.Tq, self.Length, self.Dq,
                                 int(self.TrailingStart), int(self.TrailingStop), float(self.MinPoint), int(self.StopLossSet))

    def onInit(self):
        self.writeCtaLog(u'%s策略初始化' % self.name)
        initData = self.loadBar(self.initDays)
        for bar in initData:
            self.onBar(bar)

        self.putEvent()

    # ----------------------------------------------------------------------
    def onStart(self):
        self.writeCtaLog(u'%s策略启动' % self.name)
        self.putEvent()

    # ----------------------------------------------------------------------
    def onStop(self):
        self.writeCtaLog(u'%s策略停止' % self.name)
        self.putEvent()

    # ----------------------------------------------------------------------
    def onTick(self, tick):
        lastPrice = tick.lastPrice
        #high = tick.lastPrice
        #low = tick.lastPrice
        #close = tick.lastPrice
        #req = {}
        #req['date'] = str(tick.date)
        #req['time'] = str(tick.time)
        #req['open'] = open_

        #req['volume'] = int(volume)
        #self.reqID += 1

        self.bg.updateTick(tick)
        list1 = self.wfft.onNewTick(lastPrice, int(self.BarsSinceEntry), int(self.pos))
        if len(list1) == 3:
            direction = int(list1[0])
            price = list1[1]
            vol = int(list1[2])
            if direction == 1:
                ll = self.buy(price, vol)
                '''if len(ll) > 0:
                    self.BarsSinceEntry = 0
                    if len(self.MyEntryPrice):
                        self.MyEntryPrice[0] = bar.open
                    else:
                        self.MyEntryPrice.append(bar.open)
                        #print('trade')
                    #self.pos = 1'''
            elif direction == 2:
                ll = self.short(price, vol)
                '''if len(ll) > 0:
                    self.BarsSinceEntry = 0
                    if len(self.MyEntryPrice):
                        self.MyEntryPrice[0] = bar.open
                    else:
                        self.MyEntryPrice.append(bar.open)
                    #print('trade')
                    #self.pos = -1'''
            elif direction == 3:
                self.sell(price, vol)
                #self.pos = 0
                '''self.BarsSinceEntry = 0
                self.MyEntryPrice = []'''
            elif direction ==4:
                self.cover(price, vol)
                #self.pos = 0
                '''self.BarsSinceEntry = 0
                self.MyEntryPrice = []'''


    # ----------------------------------------------------------------------
    def onBar(self, bar):
        #self.bg.updateBar(bar)
        date = bar.date.encode('utf-8')
        time = bar.time.encode('utf-8')
        open_ = bar.open
        close = bar.close
        high = bar.high
        low = bar.low
        volume = int(bar.volume)
        list1 = self.wfft.onNewBar(date,time, open_, high, low, close, volume, self.pos)
        if len(list1) == 3:
            direction = int(list1[0])
            price = list1[1]
            vol = int(list1[2])
            if direction == 1:
                self.buy(price, vol)
            elif direction == 2:
                ll = self.short(price, vol)
            elif direction == 3:
                self.sell(price, vol)
            elif direction ==4:
                self.cover(price, vol)

    def onOrder(self, order):
        pass

        # ----------------------------------------------------------------------

    def onTrade(self, trade):
        if trade.offset == OFFSET_OPEN and trade.direction==DIRECTION_LONG:
            self.BarsSinceEntry = 0
            self.pos = 1
            self.wfft.onNewTrade(trade.price,True)
        elif trade.offset == OFFSET_OPEN and trade.direction==DIRECTION_SHORT:
            self.BarsSinceEntry = 0
            self.pos = -1
            self.wfft.onNewTrade(trade.price,True)
        else:
            self.BarsSinceEntry = 0
            self.pos = 0
            self.wfft.onNewTrade(trade.price,False)



    def onStopOrder(self, so):
        pass
