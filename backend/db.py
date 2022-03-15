import sqlalchemy
from sqlalchemy import create_engine, MetaData, inspect, Table, Column, String, Date

STOCK_DATABASE_URI = 'sqlite:///stocks.db'

stock_db_engine = create_engine(STOCK_DATABASE_URI)
stock_db_meta = MetaData(bind=stock_db_engine)
MetaData.reflect(stock_db_meta)
stock_db_conn = stock_db_engine.connect()
stock_db_insp = inspect(stock_db_engine)
prev_queries = Table(
    'Previous Queries', 
    stock_db_meta,
    Column('ticker', String),
    Column('start', Date), 
    Column('end', Date),
)
stock_db_meta.create_all(stock_db_engine)
print(stock_db_engine.table_names())