import yfinance as yf
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import json
import sqlalchemy
from datetime import datetime
from sqlalchemy import create_engine, MetaData, inspect, Table, Column, Date
from sqlalchemy.sql import select

# GLOBAL VARIABLES
OPEN_COLUMN = 0
VOLUME_COLUMN = 5
STOCK_DATABASE_URI = 'sqlite:///stocks.db'
TICKER_COL = 0
START_COL = 1
END_COL = 2
SIZE_DATE_SPLICE = 10
DAILY = '1d'
WEEKLY = '1wk'
MONTHLY = '1mo'
# set of rules needed for weekly manipulation
SORT_LOGIC = {
    'Open'  : 'first',
    'High'  : 'max',
    'Low'   : 'min',
    'Close' : 'last',
    'Volume': 'sum'
}

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


def str_to_date(val : str):
    return datetime.strptime(val, '%Y-%m-%d').date()

def request_and_scrub_data(ticker, start, end, conn, interval):
    # fetch from api and POST into database if not found in database
    stock_data = yf.Ticker(ticker)
    stock_data = stock_data.history(start=start, end=end, interval=DAILY)
    print(stock_data.size)
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
    if interval != DAILY:
        data = fetch_data_from_db(ticker, start, end, interval)
    else:
        # conert from pandas DF to JSON, stock data is not from our DB but from the API
        stock_data = stock_data.to_json(orient="index")
        data = json.loads(stock_data)
    return data

def fetch_data_from_db(ticker, start, end, interval):
    print("FETCHED DATA FROM DB")
    # if interval daily do below, if weekly do weekly query not daily, if monthly do monthly query not daily
    stock_data = pd.read_sql_query(
        sql=("""
        SELECT * FROM {}
        WHERE date >= '{}' AND date <= '{}'
        ORDER BY date;""".format(ticker, start, end)
        ),
        con=stock_db_engine
    )
    stock_data.Date = pd.to_datetime(stock_data.Date)
    
    if interval == WEEKLY:
        offset = pd.offsets.timedelta(days=-6)
        test_data = stock_data
        stock_data.set_index(keys='Date', inplace=True)
        stock_data = stock_data.resample('W', kind='timestamp', loffset=offset).apply(SORT_LOGIC)
        print(stock_data)

    elif interval == MONTHLY:
        offset = pd.offsets.timedelta(days=-30)
        test_data = stock_data
        stock_data.set_index(keys='Date', inplace=True)
        stock_data = stock_data.resample('M', kind='timestamp', loffset=offset).apply(SORT_LOGIC)
        print(stock_data)

    else:
        stock_data.set_index('Date', inplace=True)
    
    stock_data = stock_data.to_json(orient="index", date_format="epoch")
    data = json.loads(stock_data)
    return data

def start_not_found_request_data(ticker, start, early_end, end, conn, interval):
    print("START NOT FOUND, MADE REQUEST, ADDED TO DB, AND FETCHED FROM DB")
    stock_data = yf.Ticker(ticker)
    stock_data = stock_data.history(start=start, end=early_end, interval=DAILY)
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
            "end" : str_to_date(early_end)
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
    data = fetch_data_from_db(ticker, start, end, interval)
    return data

def end_not_found_request_data(ticker, start, late_start, end, conn, interval):
    print("END NOT FOUND, MADE REQUEST, ADDED TO DB, AND FETCHED FROM DB")
    stock_data = yf.Ticker(ticker)
    stock_data = stock_data.history(start=late_start, end=end, interval=DAILY)
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
            "start" : str_to_date(late_start), 
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
    data = fetch_data_from_db(ticker, start, end, interval)
    return data

@app.get("/")
async def read_query(
    ticker : str = "", 
    start : str = "", 
    end : str = "", 
    interval : str = ""
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
            data = fetch_data_from_db(ticker, start, end, interval)
            return data
            
        elif earliest_start_date[TICKER_COL] == None and latest_end_date[TICKER_COL] != None:
            data = start_not_found_request_data(ticker, start, latest_end_date[START_COL], end, stock_db_engine, interval)
            return data

        elif earliest_start_date[TICKER_COL] != None and latest_end_date[TICKER_COL] == None:
            data = end_not_found_request_data(ticker, start, earliest_start_date[END_COL], end, stock_db_engine, interval)
            return data

        elif earliest_start_date[TICKER_COL] == None and latest_end_date[TICKER_COL] == None:
            print("FETCHED DATA FROM API")
            data = request_and_scrub_data(ticker, start, end, stock_db_engine, interval)
            return data
    else:
        return request_and_scrub_data(ticker, start, end, stock_db_engine, interval)