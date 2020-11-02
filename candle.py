import pandas as pd
from alpha_vantage.timeseries import TimeSeries
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import mplfinance as mpf
import Prep
import ta 
#get data from fx
api_key = 'J2443HCF3V58552B'
period = 60
fx = TimeSeries(key=api_key, output_format='pandas')
fig = mpf.figure(style='charles',figsize=(7,8))
ax1 = fig.add_subplot(2,1,1)
ax2=fig.add_subplot(2,1,2)

def animate(i):
    fx_data,fx_meta = fx.get_intraday(symbol='USDZAR', interval='1min',outputsize='full')
    fx_data = Prep.prepTS(fx_data,fx_meta)
    fx_complete = ta.add_all_ta_features(fx_data,'Open','High','Close','Low','Volume',fillna=False)
    ax1.clear()
    mpf.plot(fx_data,ax=ax1,type='candle',mav=(5))
    ax2.clear()
    ax2.plot(fx_complete.trend_macd,label='macd')
    ax2.plot(fx_complete.trend_macd_signal,label='macd_sig')
    ax2.legend()
ani = animation.FuncAnimation(fig,animate,interval=60000)
plt.show()

