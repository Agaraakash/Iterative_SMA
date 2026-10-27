import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
class SMABacktester():
    def __init__(self,symbol,SMA_S,SMA_L,start,end,percent_down,cool_down):
        self.symbol=symbol
        self.SMA_S=SMA_S
        self.SMA_L=SMA_L
        self.start=start
        self.end=end
        self.percent_down=percent_down
        self.cooldown=cool_down
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
        data = self.data2.copy().dropna()
    
        x = self.percent_down
    
        data["High_20_cutoff"] = (
            data["Close"].rolling(20).max() * (1 - x / 100)
        )
    
        data.dropna(inplace=True)
    
        close = data["Close"].squeeze()
        cutoff = data["High_20_cutoff"].squeeze()
        sma_s = data["SMA_S"].squeeze()
        sma_l = data["SMA_L"].squeeze()
    
        # Your existing entry condition
        data["base_position"] = np.where(
            (sma_s > sma_l) & (close >= cutoff),
            1,
            0
        )
    
        # NEW: Price crosses from above SMA_S to below SMA_S
        data["exit_signal"] = (
            (close.shift(1) >= sma_s.shift(1)) &
            (close < sma_s) &
            (sma_s > sma_l)
        )
    
        # NEW: Exit and stay out for cooldown trading days
        position = []
        cooldown = 0
    
        for i in range(len(data)):
    
            if cooldown > 0:
                position.append(0)
                cooldown -= 1
    
            elif data["exit_signal"].iloc[i]:
                position.append(0)
                cooldown = self.cooldown
    
            else:
                position.append(data["base_position"].iloc[i])
    
        data["position"] = position
    
        # Your existing return calculations
        data["strategy"] = data["returns"] * data["position"].shift(1)
        data.dropna(inplace=True)
    
        data["returnsbh"] = data["returns"].cumsum().apply(np.exp)
        data["returnstrategy"] = data["strategy"].cumsum().apply(np.exp)
    
        perf = data["returnstrategy"].iloc[-1]
        outpref = perf - data["returnsbh"].iloc[-1]
    
        self.results = data
    
        std = data["strategy"].std() * np.sqrt(252)
        ret = np.exp(data["strategy"].sum())
    
        return ret, std, round(outpref, 6)

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