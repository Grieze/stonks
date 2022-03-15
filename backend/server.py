import yfinance as yf
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import json
import sqlalchemy
from datetime import datetime
from sqlalchemy import create_engine, MetaData, inspect, Table, Column, Date
from sqlalchemy.sql import select

# uvicorn server:app --reload
# GLOBAL VARIABLES
OPEN_COLUMN = 0
VOLUME_COLUMN = 5
STOCK_DATABASE_URI = 'sqlite:///stocks.db'
DAILY_CODE = '1d'
TICKER_COL = 0
START_COL = 1
END_COL = 2
SIZE_DATE_SPLICE = 10

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

stock_db_engine = create_engine(STOCK_DATABASE_URI)
stock_db_meta = MetaData(bind=stock_db_engine)
MetaData.reflect(stock_db_meta)
stock_db_conn = stock_db_engine.connect()
stock_db_insp = inspect(stock_db_engine)
print(stock_db_engine.table_names())
prev_queries_table = stock_db_meta.tables['Previous Queries']
prev_queries_insert = prev_queries_table.insert()

"""
TODO:
Need to create
- function for weekly data 
- function for monthly data
"""

def str_to_date(val : str):
    return datetime.strptime(val, '%Y-%m-%d').date()

def request_and_scrub_data(ticker, start, end, conn):
    # fetch from api and POST into database if not found in database
    stock_data = yf.Ticker(ticker)
    stock_data = stock_data.history(start=start, end=end, interval=DAILY_CODE)
    # don't need to have the dividends and stock splits columns so we leave them out
    stock_data = stock_data.iloc[:,OPEN_COLUMN:VOLUME_COLUMN]
    # round off unneccesary data
    stock_data = stock_data.round(2)
    # set dates to get rid of unncessary HH:MM:SS:MS format
    stock_data.reset_index(inplace=True)
    stock_data['Date'] = stock_data['Date'].dt.date
    stock_data.set_index('Date', inplace=True)
    """ 
    Each table name will be a ticker name because we are querying tickers
    and putting daily data into the ticker's table only, we get weekly and 
    monthly data by pulling data from the DB and manipulating it via pandas
    """
    stock_data.to_sql(name=ticker, con=conn, if_exists='append')
    # Insert the ticker + dates so we have a historical timestamp of already known stored data
    stock_db_conn.execute(
        prev_queries_insert, 
        {
            "ticker" : ticker, 
            "start" : start, 
            "end" : end
        }
    )
    stock_db_conn.execute(
        """
        DELETE from {}
        WHERE ROWID NOT IN (SELECT MIN(ROWID)
        FROM {}
        GROUP BY date)
        """.format(ticker, ticker)
    )
    print(stock_db_engine.table_names())
    stock_data = stock_data.to_json(orient="index")
    data = json.loads(stock_data)
    return data

def fetch_data_from_db(ticker, start, end):
    print("FETCHED DATA FROM DB")
    stock_data = pd.read_sql_query(
        sql=("""
        SELECT * FROM {}
        WHERE date >= '{}' AND date <= '{}'
        ORDER BY date;""".format(ticker, start, end)
        ),
        con=stock_db_engine
    )
    stock_data.Date = pd.to_datetime(stock_data.Date)
    stock_data.Date = (stock_data.Date - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')
    stock_data.set_index('Date', inplace=True)
    print(stock_data)
    stock_data = stock_data.to_json(orient="index", date_format="epoch")
    data = json.loads(stock_data)
    return data

def start_not_found_request_data(ticker, start, end, conn):
    print("START NOT FOUND, MADE REQUEST, ADDED TO DB, AND FETCHED FROM DB")
    stock_data = yf.Ticker(ticker)
    stock_data = stock_data.history(start=start, end=end, interval=DAILY_CODE)
    stock_data = stock_data.iloc[:,OPEN_COLUMN:VOLUME_COLUMN]
    stock_data = stock_data.round(2)
    stock_data.reset_index(inplace=True)
    stock_data['Date'] = stock_data['Date'].dt.date
    stock_data.set_index('Date', inplace=True)
    stock_data.to_sql(name=ticker, con=conn, if_exists='append')
    # Insert the ticker + dates so we have a historical timestamp of already known stored data
    stock_db_conn.execute(
        prev_queries_insert, 
        {
            "ticker" : ticker, 
            "start" : start, 
            "end" : str_to_date(end)
        }
    )
    stock_db_conn.execute(
        """
        DELETE from {}
        WHERE ROWID NOT IN (SELECT MIN(ROWID)
        FROM {}
        GROUP BY date)
        """.format(ticker, ticker)
    )            
    data = fetch_data_from_db(ticker, start, end)
    return data

def end_not_found_request_data(ticker, start, end, conn):
    print("END NOT FOUND, MADE REQUEST, ADDED TO DB, AND FETCHED FROM DB")
    stock_data = yf.Ticker(ticker)
    stock_data = stock_data.history(start=start, end=end, interval=DAILY_CODE)
    stock_data = stock_data.iloc[:,OPEN_COLUMN:VOLUME_COLUMN]
    stock_data = stock_data.round(2)
    stock_data.reset_index(inplace=True)
    stock_data['Date'] = stock_data['Date'].dt.date
    stock_data.set_index('Date', inplace=True)
    stock_data.to_sql(name=ticker, con=conn, if_exists='append')
    # Insert the ticker + dates so we have a historical timestamp of already known stored data
    stock_db_conn.execute(
        prev_queries_insert, 
        {
            "ticker" : ticker, 
            "start" : str_to_date(start), 
            "end" : end
        }
    )
    # delete any duplicate dates we may add since end date will overlap with existing data
    stock_db_conn.execute(
        """
        DELETE from {}
        WHERE ROWID NOT IN (SELECT MIN(ROWID)
        FROM {}
        GROUP BY date)
        """.format(ticker, ticker)
    )            
    data = fetch_data_from_db(ticker, start, end)
    return data

@app.get("/")
async def read_query(
    ticker : str = "TSLA", 
    start : str = "2012-09-01", 
    end : str = "2012-12-01", 
    interval : str = "1d"
    ):
    start = str_to_date(start)
    end = str_to_date(end)
    # Check if the table exists, if it does query DB and make API requests if data missing
    if stock_db_insp.has_table(ticker):
        # Need reflect in order for DB to be read and not return any errors 
        # server crashes without this line of code
        MetaData.reflect(stock_db_meta)
        # see if start date already in db
        earliest_start_date = stock_db_conn.execute(
            """
            SELECT ticker, MIN(start), MIN(end) FROM 'Previous Queries'
            WHERE ticker = '{}' AND start <= '{}' AND end >= {};
            """.format(ticker, start, start)
        )
        # see if end date already in db
        latest_end_date = stock_db_conn.execute(
            """
            SELECT ticker, min(start), MIN(end) FROM 'Previous Queries'
            WHERE ticker = '{}' AND start <= '{}' AND end >= '{}';
            """.format(ticker, end, end)
        )
        
        earliest_start_date = [row for row in earliest_start_date.first()]
        latest_end_date = [row for row in latest_end_date.first()]
        print(earliest_start_date)
        print(latest_end_date)

        if (earliest_start_date[TICKER_COL] != None and latest_end_date[TICKER_COL] != None):
            data = fetch_data_from_db(ticker, start, end)
            return data
            
        elif earliest_start_date[TICKER_COL] == None and latest_end_date[TICKER_COL] != None:
            data = start_not_found_request_data(ticker, start, latest_end_date[START_COL], stock_db_engine)
            return data

        elif earliest_start_date[TICKER_COL] != None and latest_end_date[TICKER_COL] == None:
            data = end_not_found_request_data(ticker, earliest_start_date[END_COL], end, stock_db_engine)
            return data

        elif earliest_start_date[TICKER_COL] == None and latest_end_date[TICKER_COL] == None:
            print("FETCHED DATA FROM API")
            data = request_and_scrub_data(ticker, start, end, stock_db_engine)
            return data
    else:
        return request_and_scrub_data(ticker, start, end, stock_db_engine)