import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import datetime as dt
import yfinance as yf
import os
plt.style.use('ggplot')

#1

data_folder= ''

sentiment_df =  pd.read_csv(os.path.join(data_folder, 'sentiment_data.csv'))

sentiment_df['date'] = pd.to_datetime(sentiment_df['date'])

sentiment_df = sentiment_df.set_index(['date', 'symbol'])

sentiment_df['engagement_ratio'] = sentiment_df['twitterComments']/sentiment_df['twitterLikes']

sentiment_df = sentiment_df[(sentiment_df['twitterLikes']>20)&(sentiment_df['twitterComments']>10)]

sentiment_df

#2 Aggregate Monthly and calcultae average sentiment for the month

aggragated_df = sentiment_df.reset_index('symbol').groupby([pd.Grouper(freq='M'), 'symbol'])[['engagement_ratio']].mean()

aggragated_df['rank'] = (aggragated_df.groupby(level=0)['engagement_ratio'].transform(lambda x: x.rank(ascending=False)))

aggragated_df


#3 Select TOP 5 for each month based on their cross sectional 

filtered_df =  aggragated_df[aggragated_df['rank']<6].copy()

filtered_df = filtered_df.reset_index(level=1)

filtered_df.index = filtered_df.index+pd.DateOffset(1)

filtered_df = filtered_df.reset_index().set_index(['date', 'symbol'])

filtered_df.head(20)

#4 Extract the stocks to form portfolios with at the start of each new month
dates = filtered_df.index.get_level_values('date').unique().tolist()

fixed_dates = {}

for d in dates:

	fixed_dates[d.strftime('%Y-%m-%d')] = filtered_df.xs(d, level=0).index.tolist()

fixed_dates
#5 Download Fresh Prices of the shotlisted stocks
stocks_list = sentiment_df.index.get_level_values('symbol').unique().tolist()

# Calculate portfolio returns with monthly rebalancing using available stocks

prices_df = yf.download(tickers=stocks_list, start='2021-01-01', end='2023-03-01')

# Assume `prices_df` is the DataFrame containing the price data
# Remove 'ATVI' from the columns

# Check if 'ATVI' is in the columns
if 'ATVI' in prices_df.columns.get_level_values(1):
    # Drop 'ATVI' from the DataFrame
    prices_df = prices_df.drop(columns='ATVI', level=1)

#6  Calculate portfolio returns with monthly rebalancing
returns_df = np.log(prices_df['Adj Close']).diff().dropna()
portfolio_df =  pd.DataFrame()

for start_date in fixed_dates.keys():

	end_date = (pd.to_datetime(start_date)+pd.offsets.MonthEnd()).strftime('%Y-%m-%d')
	cols = fixed_dates[start_date]
	temp_df = returns_df[start_date:end_date][cols].mean(axis=1).to_frame('portfolio_return')
	portfolio_df = pd.concat([portfolio_df, temp_df], axis=0)



#7 Download NASDAQ QQQ prices and calculate returns to compare to our strategy

#qqq_df = yf.download(tickers='QQQ', start='2021-01-01', end='2023-03-01')

#qqq_ret = np.log(qqq_df['Adj Close']).diff().to_frame('nasdaq_return')

#portfolio_df = portfolio_df.merge(qqq_ret, left_index=True, right_index=True)

portfolio_df

#8 Visualise

portfolios_cumlative_ret= np.exp(np.log1p(portfolio_df).cumsum()).sub(1)

portfolios_cumlative_ret.plot(figsize=(16,6))

plt.title('Twitter Sentiment Ratio Startegy Return Over Time')

plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(1))

plt.ylabel('Return')

plt.show()


