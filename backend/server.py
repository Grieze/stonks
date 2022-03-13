import yfinance as yf
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import json
import sqlalchemy
from datetime import datetime
from sqlalchemy import create_engine, MetaData, inspect
from sqlalchemy.sql import select

# uvicorn server:app --reload
# GLOBAL VARIABLES
OPEN_COLUMN = 0
VOLUME_COLUMN = 5
STOCK_DATABASE_URI = 'sqlite:///stocks.db'

# API set up
app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

stock_db_engine = create_engine(STOCK_DATABASE_URI, echo=True)
stock_db_meta = MetaData(bind=stock_db_engine)
MetaData.reflect(stock_db_meta)
stock_db_conn = stock_db_engine.connect()
stock_db_insp = inspect(stock_db_engine)
print(stock_db_engine.table_names())
prev_queries_table = stock_db_meta.tables['Previous_Queries']
prev_queries_insert = prev_queries_table.insert()
print(prev_queries_insert)

"""
TODO:
Need to create
- insert into previous queries table function
- function for weekly data 
- function for monthly data
- function for querying and appending ticker table if necessary 
  by querying both ticker and previous queries table

"""

@app.get("/")
async def read_query(
    ticker : str = "NFLX", 
    start : str = "2022-01-03", 
    end : str = "2022-03-31", 
    interval : str = "1d"
    ):
    # check the database first
    print(stock_db_engine.table_names())
    # want to check if the table exists and if so, do the dates exist in the ticker table
    if stock_db_insp.has_table(ticker):
        """
        Problem with selection line, after code creates a table with ticker,
        it spits out an error saying the table doesn't exist and gives off an internal server error
        """
        ticker_selection = stock_db_meta.tables[ticker]
        ticker_query = select([
            ticker_selection.c.Date, 
            ticker_selection.c.Open, 
            ticker_selection.c.High, 
            ticker_selection.c.Low, 
            ticker_selection.c.Close, 
            ticker_selection.c.Volume
        ])
        hist = pd.read_sql_query(
            sql=ticker_query,
            con=stock_db_engine
        )
        start_as_date = datetime.strptime(start, '%Y-%m-%d').date()
        end_as_date = datetime.strptime(end, '%Y-%m-%d').date()
        # stock_db_conn.execute(prev_queries_insert, {"ticker" : ticker, "start" : start_as_date, "end" : end_as_date})
        # hist.Date = hist.Date.astype(str)
        print(start in hist.Date.values)
        print(end in hist.Date.values)
        return "Issue was returning pandas df object"

    # fetch from api and POST into database if not found in database
    stock_data = yf.Ticker(ticker)
    stock_data = stock_data.history(start=start, end=end, interval=interval)
    # don't need to have the dividends and stock splits columns so we leave them out
    stock_data = stock_data.iloc[:,OPEN_COLUMN:VOLUME_COLUMN]
    stock_data = stock_data.round(2)
    # Each table name will be a ticker name because we are querying tickers
    # and putting daily data into the ticker's table only, we get weekly and 
    # monthly data by pulling data from the DB and manipulating it via pandas
    stock_data.to_sql(name=ticker, con=stock_db_engine)
    stock_data = stock_data.to_json(orient="index")
    data = json.loads(stock_data)
    return data

