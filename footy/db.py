import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    DATABASE_URL = os.environ.get('CLEARDB_DATABASE_URL')

print 'DATABASE_URL=', DATABASE_URL

def getSqlAlchemyConnection(connection_string, echo=False, pool_size=6):
    if "?reconnect=true" in connection_string:
        connection_string = connection_string.replace("?reconnect=true", "?")
    engine = create_engine(connection_string, echo=echo, pool_size=pool_size, pool_recycle=3600)
    maker = sessionmaker(bind=engine)
    session = maker()
    return engine, maker, session

engine, maker, session = getSqlAlchemyConnection(DATABASE_URL)
