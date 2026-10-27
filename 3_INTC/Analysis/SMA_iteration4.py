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
        data = self.data2.copy()
    
        # Remove duplicate column names
        data = data.loc[:, ~data.columns.duplicated()]
    
        x = self.percent_down
    
        # Ensure Close is a single Series
        close_data = data["Close"]
        if isinstance(close_data, pd.DataFrame):
            close_data = close_data.iloc[:, 0]
    
        data["Close"] = close_data
    
        # Fast moving average
        data["SMA_SS"] = data["Close"].rolling(10).mean()
    
        # Entry cutoffs
        data["High_20_cutoff"] = (
            data["Close"].rolling(20).max() * (1 - x / 100)
        )
    
        data["Low_20_cutoff"] = (
            data["Close"].rolling(20).min() * (1 + x / 100)
        )
    
        data.dropna(inplace=True)
    
        # Pandas Series for rolling and shift operations
        close = data["Close"].squeeze()
        high_cutoff = data["High_20_cutoff"].squeeze()
        low_cutoff = data["Low_20_cutoff"].squeeze()
        sma_ss = data["SMA_SS"].squeeze()
        sma_s = data["SMA_S"].squeeze()
        sma_l = data["SMA_L"].squeeze()
    
        # Convert to 1D arrays for entry comparisons
        close_arr = np.asarray(close).reshape(-1)
        high_cutoff_arr = np.asarray(high_cutoff).reshape(-1)
        low_cutoff_arr = np.asarray(low_cutoff).reshape(-1)
        sma_s_arr = np.asarray(sma_s).reshape(-1)
        sma_l_arr = np.asarray(sma_l).reshape(-1)
    
        # Base entry conditions
        long_cond = (
            (sma_s_arr > sma_l_arr) &
            (close_arr >= high_cutoff_arr)
        )
    
        short_cond = (
            (sma_s_arr < sma_l_arr) &
            (close_arr <= low_cutoff_arr)
        )
    
        data["base_position"] = np.select(
            [long_cond, short_cond],
            [1, -1],
            default=0
        )
    
        exit_threshold = x / 2
    
        # Existing long exit cutoff
        data["High_exit_cutoff"] = (
            close.rolling(20).max() * (1 - exit_threshold / 100)
        )
    
        long_exit_signal = (
            (close.shift(1) >= sma_s.shift(1)) &
            (close < sma_s) &
            (sma_s > sma_l) &
            (close < data["High_exit_cutoff"])
        )
    
        # Existing short exit cutoff
        data["Low_exit_cutoff"] = (
            close.rolling(20).min() * (1 + exit_threshold / 100)
        )
    
        short_exit_signal = (
            (close.shift(1) <= sma_s.shift(1)) &
            (close > sma_s) &
            (sma_s < sma_l) &
            (close > data["Low_exit_cutoff"])
        )
    
        # Exit long if price falls 20% over 8 days
        fall_8_days = close <= close.shift(8) * 0.80
    
        long_continuous_fall_exit = (
            fall_8_days &
            (data["base_position"] == 1)
        )
    
        # Exit short if price rises 20% over 8 days
        rise_8_days = close >= close.shift(8) * 1.20
    
        short_continuous_rise_exit = (
            rise_8_days &
            (data["base_position"] == -1)
        )
    
        # Moving-average crossover signals
        data["SMA_diff"] = (
            data["SMA_SS"].to_numpy().reshape(-1) -
            data["SMA_S"].to_numpy().reshape(-1)
        )
    
        # Potential maximum: SMA_SS crosses below SMA_S
        cross_down = (
            (data["SMA_diff"].shift(1) >= 0) &
            (data["SMA_diff"] < 0)
        )
    
        # Potential minimum: SMA_SS crosses above SMA_S
        cross_up = (
            (data["SMA_diff"].shift(1) <= 0) &
            (data["SMA_diff"] > 0)
        )
    
        # Crossover exits
        long_cross_exit = (
            cross_down &
            (data["base_position"] == 1)
        )
    
        short_cross_exit = (
            cross_up &
            (data["base_position"] == -1)
        )
    
        # Combine exit signals
        data["exit_signal"] = (
            long_exit_signal |
            short_exit_signal |
            long_continuous_fall_exit |
            short_continuous_rise_exit |
            long_cross_exit |
            short_cross_exit
        )
    
        # Position and cooldown logic
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
    
        # Strategy returns using previous day's position
        data["strategy"] = (
            data["returns"] * data["position"].shift(1)
        )
    
        data.dropna(inplace=True)
    
        # Cumulative returns
        data["returnsbh"] = np.exp(data["returns"].cumsum())
        data["returnstrategy"] = np.exp(data["strategy"].cumsum())
    
        perf = data["returnstrategy"].iloc[-1]
        outpref = perf - data["returnsbh"].iloc[-1]
    
        self.results = data
    
        std = data["strategy"].std() * np.sqrt(252)
        ret = np.exp(data["strategy"].sum())
    
        return ret, std, round(outpref, 6)
    def plot_results(self):
        if self.results is None:
            print("Run the test please")
        else :
            title="{}| Results using -> SMA_S={} | SMA_L{}".format(self.symbol,self.SMA_S,self.SMA_L)
            self.results[["returnsbh","returnstrategy"]].plot(title=title,figsize=(12,8))
    #now i also want tf see rolling avg graph see if that is indicator for somethign
    def roll_graph(self):
        title="{}| ROLL1={} | ROLL2={}".format(self.symbol,self.SMA_S,self.SMA_L)
        ax=self.results[["SMA_S", "SMA_L", "Close","SMA_SS"]].plot(
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