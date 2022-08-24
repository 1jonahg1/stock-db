import yfinance as yf

yahoo_data = yf.Ticker("AAPL")

# get stock info
print(yahoo_data.info)




print(yahoo_data.info['twoHundredDayAverage'])
print(yahoo_data.info['fiftyDayAverage'])
print( yahoo_data.info['previousClose'])
print( yahoo_data.info['forwardPE'])
print(yahoo_data.info['forwardEps']) 
if yahoo_data.info['dividendYield'] is not None:
    print(yahoo_data.info['dividendYield'] * 100)
else:
    print("no dividend")
