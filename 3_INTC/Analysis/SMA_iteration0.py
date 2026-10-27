import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
class SMABacktester():
    def __init__(self,symbol,SMA_S,SMA_L,start,end):
        self.symbol=symbol
        self.SMA_S=SMA_S
        self.SMA_L=SMA_L
        self.start=start
        self.end=end
        self.results=None
        self.get_data()

    def get_data(self):
        df=yf.download(self.symbol,start=self.start,end=self.end)
        # data=df.Close.to_frame()
        # print(data)
        data=df[["Close"]]
        data["returns"]=np.log(data.Close.div(data.Close.shift(1)))
        data["SMA_S"]=data.Close.rolling(self.SMA_S).mean()
        data["SMA_L"]=data.Close.rolling(self.SMA_L).mean()
        data.dropna(inplace=True)
        self.data2=data
        #this data remains same not dependent much on others or say 
        #this data is clean given things only thats why storing in self
        #makes it cool and elegant
        return data
    def test_result(self):
        #data was in self and abb elegant!
        print("hello")
        data=self.data2.copy().dropna()
        data["position"]=np.where(data["SMA_S"]>data["SMA_L"],1,-1)
        data["strategy"]=data["returns"]*data.position.shift(1)
        data.dropna(inplace=True)
        data["returnsbh"]=data["returns"].cumsum().apply(np.exp)
        data["returnstrategy"]=data["strategy"].cumsum().apply(np.exp)
        perf=data["returnstrategy"].iloc[-1]
        outpref=perf-data["returnsbh"].iloc[-1]
        self.results=data
        std=data["strategy"].std()*np.sqrt(252)
        ret=np.exp(data["strategy"].sum())
        # print(data)
        return ret,std,round(outpref,6)
        # return round(perf,6), round(outpref,6)
    def plot_results(self):
        if self.results is None:
            print("Run the test please")
        else :
            title="{}| Results using -> SMA_S={} | SMA_L{}".format(self.symbol,self.SMA_S,self.SMA_L)
            self.results[["returnsbh","returnstrategy"]].plot(title=title,figsize=(12,8))
    #now i also want tf see rolling avg graph see if that is indicator for somethign
    def roll_graph(self):
        title="{}| ROLL1={} | ROLL2={}".format(self.symbol,self.SMA_S,self.SMA_L)
        ax=self.results[["SMA_S", "SMA_L", "Close"]].plot(
            title=title,
            figsize=(12, 8),
        )
        self.results["position"].plot(
            ax=ax,
            secondary_y=True,
            color="red",
            label="Position"
        )
    
        plt.show()