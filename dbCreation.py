# This file ought to handle all the database stuff

from sqlalchemy import create_engine
from sqlalchemy import MetaData, Table, String, Column, Text, DateTime, Boolean, Integer, ForeignKey
# from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

def connect2engine():
    """
    Connecting to PostgreSQL server at localhost using psycopg2 DBAPI
    Syntax: <username>:<password>@<host>/<dbname>
    Engine object is how to interact with database

    .. note:: Passwort of postgres changed from sudo pw to a new one with "\password postgres"

    :returns: engine, metadata
    """
    engine=create_engine("postgresql+psycopg2://postgres:climbingdbPW!@localhost/sandbox")
    engine.connect()
    # print(engine)
    metadata = MetaData()
    return engine, metadata


        
def init_tables(metadata):
    """
    A function to create the Tables LOCATIONS, ROUTES, ASCENTS.
    """
    
    location = Table('LOCATIONS', metadata, 
                     Column('cragID', Integer, primary_key=True),
                     Column('crag', String(50), nullable=False), # e.g. Waldkopf
                     Column('area', String(50), nullable=False), # e.g. Frankenjura
                     Column('country', String(30), nullable=False), # e.g. Germany
                     Column('cragnote', Text, nullable=True) # e.g. "Very cool overhang"
    )
    
    route = Table('ROUTES', metadata,
                  Column('routeID', Integer, primary_key=True), # RouteID is unique
                  Column('name', String(50), nullable=False), # A non-unique name of a route
                  Column('grade', String(10), nullable=False), # A route must have a proposed grade
                  Column('notes', Text, nullable=True), # string extended further and futher
                  Column('fkCragID', ForeignKey("LOCATIONS.cragID")) # points to cragID in LOCATIONS DB
    )

    ascent = Table('ASCENTS', metadata,
                   Column('ascentID', Integer, primary_key=True), # not sure if AscentID is of use
                   Column('fkRouteID', Integer, ForeignKey(route.c.routeID)), # points to ROUTES table
                   Column('grade', String(10), nullable=True), # Each route can have a personal grade
                   Column('style', String(10), nullable=True), # o.s., F., trad, etc.
                   Column('shortnote', String(10), nullable=True), # hard, soft, 2. Go, etc.
                   Column('date', DateTime, default=datetime.now),
                   Column('project', Boolean, default=False),
                   Column('stars', Integer, nullable=True) # stars = 0, 1, 2, or 3
    )

    metadata.drop_all(engine)
    metadata.create_all(engine)

    
if __name__=="__main__":
    (engine, metadata) = connect2engine()
    init_tables(metadata)
