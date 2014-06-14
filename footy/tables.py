from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation

DeclarativeBase = declarative_base()

class Entrant(DeclarativeBase):
    __tablename__ = 'entrant'

    __table_args__ = {}

    #column definitions
    id = Column(u'id', INTEGER(), primary_key=True, nullable=False)
    name = Column(u'name', VARCHAR(length=255))
    email = Column(u'email', VARCHAR(length=255))
    affiliation = Column(u'affiliation', VARCHAR(length=255))

    #relation definitions


class EntrantSelection(DeclarativeBase):
    __tablename__ = 'entrant_selection'

    __table_args__ = {}

    #column definitions
    entrant_id = Column(u'entrant_id', INTEGER(), primary_key=True, nullable=False)
    selection_id = Column(u'selection_id', INTEGER(), primary_key=True, nullable=False)
    selection_value = Column(u'selection_value', VARCHAR(length=255))

    #relation definitions


class Game(DeclarativeBase):
    __tablename__ = 'game'

    __table_args__ = {}

    #column definitions
    id = Column(u'id', INTEGER(), primary_key=True, nullable=False)
    date = Column(u'date', DATE())
    title = Column(u'title', VARCHAR(length=255))
    team1 = Column(u'team1', VARCHAR(length=128))
    team2 = Column(u'team2', VARCHAR(length=128))
    group_id = Column(u'group_id', INTEGER())
    stage_id = Column(u'stage_id', INTEGER())

    #relation definitions


class Group(DeclarativeBase):
    __tablename__ = 'group'

    __table_args__ = {}

    #column definitions
    id = Column(u'id', INTEGER(), primary_key=True, nullable=False)
    name = Column(u'name', VARCHAR(length=1))

    #relation definitions


class Selection(DeclarativeBase):
    __tablename__ = 'selection'

    __table_args__ = {}

    #column definitions
    id = Column(u'id', INTEGER(), primary_key=True, nullable=False)
    stage_id = Column(u'stage_id', INTEGER())
    game_id = Column(u'game_id', INTEGER())
    description = Column(u'description', VARCHAR(length=255))

    #relation definitions


class Stage(DeclarativeBase):
    __tablename__ = 'stage'

    __table_args__ = {}

    #column definitions
    id = Column(u'id', INTEGER(), primary_key=True, nullable=False)
    name = Column(u'name', VARCHAR(length=255))

    #relation definitions


