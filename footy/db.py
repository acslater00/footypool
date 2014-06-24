import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sqlalchemy.orm

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

def _is_session_type(obj):
    if hasattr(sqlalchemy.orm, 'Session') and isinstance(obj, sqlalchemy.orm.Session):
        return True
    if hasattr(sqlalchemy.orm, 'ScopedSession') and isinstance(obj, sqlalchemy.orm.ScopedSession):
        return True
    if hasattr(sqlalchemy.orm, 'scoping') and hasattr(sqlalchemy.orm.scoping, 'ScopedSession') and isinstance(obj, sqlalchemy.orm.scoping.ScopedSession):
        return True
    return False

def with_session(maker, use_scoped=False):
    """Decorator that generates an sqlalchemy connection as the
    first argument to a given function, or allows one to be passed
    explicitly

    Usage:

        @with_session(maker)
        def some_function(session, id):
            return session.query(Table).get(id)

        # both of these calls work...
        some_function(1)
        some_function(session_in_use, 1)
    """
    assert maker, 'provided sessionmaker cannot be None'
    def wrap(fn):
        def newfn(*args, **kwargs):
            if len(args) > 0 and _is_session_type(args[0]):
                return fn(*args, **kwargs)
            else:
                try:
                    if use_scoped:
                        session = scoped_session(maker)
                    else:
                        session = maker()
                    return fn(session, *args, **kwargs)
                finally:
                    session.close()
        return newfn
    return wrap

engine, maker, session = getSqlAlchemyConnection(DATABASE_URL)
session.close()
