# Candlestick Charts.

***Important***:
This project involves writing a simple back-end and front-end for an application that displays prices of stocks in a graph.

The back-end involves getting price data from a free source (yahoo) and provide it as JSON to a Javascript front-end. The front-end involves displaying the data as a candlestick chart. 

We do NOT expect you to write everything from scratch. There are high quality, free libraries that get stock price data from yahoo and make it available in multiple formats. There are free libraries that work with multiple front-end frameworks that display candlestick charts.

We expect you to make good choices regarding which library to use and explain why you chose what you chose. We expect you to write code like you would write in production. This means code should be written for other programmers to understand and documented when necessary. You should try to write your code in a manner that the how is self-explanatory and document the why.

If you need clarification or if you get stuck, call me and I will help.

### The Problem

#### The Front End
Create a web page on which there are 4 inputs. 
One allows a user to type in the ticker symbol for a stock. 
The second input is a start date. 
The third input is an end date. 
The fourth input allows a user to choose between daily, weekly or monthly data.

If the user types in a ticker symbol that does not exist, or a start date that is the same or later than the end date, the page should let the user know that there is an error. If the user types in a start date earlier than the earliest date for which we have data or later than the latest date for which we have data, then the date entered should be replaced with the appropriate date when the graph is drawn.

If the user requests daily data, display daily data i.e. daily open price, high price, low price, close price and volume (number of shares traded). If the user requests weekly data, display weekly data i.e. weekly open price, high price, low price, close price and volume. Note the weekly open price is the open price of the first day in the week. The weekly high (low) price is the highest high (lowest low) price of all the high (low) prices during the week. The weekly close price is the close price of the last day in the week. The same applies for monthly data. Similarly, the volume (number of shares traded) for the week (month) is the sum of the number of shares traded each day during the week (month). Note that you may not have to do any calculation. You can request daily, weekly or monthly data from the libraries that get stock price data from Yahoo.

The area of the page devoted to showing stock data should be divided into 2 seconds, Approximately 80% of the height taken up by the first section and the remainder by the second section.

The first section (approximately top 80% of the area devoted to graphing stock data) should display a candlestick chart of the stock price data. For a description of what a candlestick chart is see [Wikipedia](https://en.wikipedia.org/wiki/Candlestick_chart) and/or  [Investopedia](https://www.investopedia.com/trading/candlestick-charting-what-is-it/).

In the second section (bottom 20% of the area devoted to graphing data) should display a bar chart of the volume (number of shares) traded on the specific day/week/month. The bar representing a period's week should line up vertically with the candlestick representing the prices during that period. Volume bars for periods when the close price > open price should be green. Volume bars for periods when close price < open price should be red. Volume bars for periods when open price = close price should be black.

When the mouse hovers over the grapyh, a the mouse cursor should be replaced with crosshairs and a vertical line should appear that goes through the center of the crosshairs. The vertical line should show connect the candlestick for that day and the volume bar for that day in the bottom section of the graph.

#### The Back End
The front end should query the back end for the data. 

The back end should provide a single REST endpoint that returns the data requested. The back-end queries a free source of data (use yahoo finance of alphavantage) for the data. The back end should only request data from the data source once. 

When the data is received for a particular ticker/date range, it should be saved in a SQLite database by the back-end. If the data has previously been requested and exists in the database, the data source should not be queried again but simply returned from the database. 

Let's pretend that we get charged by the data provider for every data point, say 1/10 cent per stock day that we request data and we want to minimize these costs. If the data requested is partially available, say data for SPY is requested between Jan 1, 2020 and Dec 31, 2022 and you already have data in the database for SPY betwen Jan 1, 2022 and Dec 31, 2022, only request data for SPY for the date range Jan 1, 2020 and Dec 31, 2021 from the data source used and then save this data into the back-end database. Then return the data for the entire range requested to the front end by chaining the data gotten from the external data source and the data already in the database. A caveat to consider is that if that there are regular holidays when all stocks don't trade and there are days when the market is open but a particular stock does not trade. You need to account for this when you decide what to query. 

One solution could for example be having two fields in the table of stock prices, one which is true if the date is a holiday and another which is true if it wasn't a holiday but that stock didn't trade. You can get a list of dates on which the stock market was open by requesting a long time history of an index like the Dow Jones. You will get data for every day the stock market was open. You will know a stock didn't trade on a non-holiday date if you request data for an interval, the Dow Jones timeseries has data for that date but the data returned by the endpoint has not data for that date.

Another solution could involve having a second table where you store stock, start date and end date tuples every time you make a request for price data. Assume data for all tuples in this table already exists in the price table and only request data for other time periods.

The back-end should only request daily data from the free-data source. If monthly or weekly data is requested, generate the data from the daily data and return it. 

The Open price for weekly/monthly data is the open price on the first day of the week/month. The Close price for weekly/monthly data is the close price of the last day of the week/month. 
The high/low price for the week month is the highest/lowest of the daily high/low prices for the week/month. 

Note that exchanges are not open every day so the first/last trading date in the month may not be the first/last date of the month. Similarly the first/last trading day in a week may not be the Monday or Friday. 


#### Other details
We expect that you will use React or Vue for the front-end and Python for the back-end. You may use any open source library or component. You may not use closed source libraries. If you do not make extensive use of open source libraries, this project may take an inordinate amount of time. In fact, while this project may overwhelm at first, it is in fact a straightforward stitching together of a few open source libraries. 

You may not generate an image to display in the back-end and display this image in the front-end. The back-end should be get data from yahoo and provide it to the front end as JSON. The front-end should then display this data.

Note that there are multiple open-source libraries that can display the data properly. All you need to do is display the appropriate graphing component on the page ensure the data is in a format the component can use and provide it to the component.

In the front-end, please use a state management solution (for example, if you build using React, use Redux or MobX) assuming this will turn into a large app and getting new data means updating many different components as the app grows. 

The back-end should be written using [fastapi](https://fastapi.tiangolo.com/). Database access should be using [SQLAlchemy](https://www.sqlalchemy.org/) or [SQLModel](https://sqlmodel.tiangolo.com/). You should use [typer](https://typer.tiangolo.com/) to create commands that start the back-end and the front end.

There are multiple open-source libraries, in some cases small pieces of larger libraries that get stock price data from yahoo and alphavantage. You should get the data using one of these libraries. If you try to use these apis directly, you may end up spending a fair amount of time dealing with edge cases where they sometimes behave in strange ways.

We are deliberately not suggesting specific front-end components or open-source libraries. Part of what we are expecting is that you will choose one appropriately and describe why you chose what you chose and why you did not choose the alternatives. However, if your google-fu is failing you, and you would like some suggestions, get in touch and I will help.


***NOTE:***
Please ensure you include a README file with detailed instructions describing how to build and run your project. The instructions should be sufficient for an experienced programmer who has never written a line of Javascript of Python (or other language or tool you may use) to build and run your code.

In a perfect world, you will send us docker file that creates a server that serves your front-end artifacts and serves up the JSON data. This is ideal but not required. We also need instructions on how to build and run your code, starting from checking out your code from source control.

For both the front-end and back-end, please ensure that you write code as you would if you were writing production code. Code should be production quality. We are evaluating you on whether you understand the difference between extensible, production quality code and the code a student would write.
