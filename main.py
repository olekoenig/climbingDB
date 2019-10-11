#!/usr/bin/env python3

"""
main can be used directly from the command line to query the database
see ./main.py --help
"""

from argparse import ArgumentParser
from argparse import RawTextHelpFormatter

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import MetaData

from ascent import Ascent, Base
from climbingQuery import ClimbingQuery # Get query functions


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


def createTablesStartSession(engine):
    Base.metadata.create_all(engine, checkfirst=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def arguments():
    parser = ArgumentParser(description = ("Ole's climbing database"),
                             formatter_class=RawTextHelpFormatter)
    parser.add_argument('-g','--grade', type=str,
                         help=("Set grades to display in Frensh, UIAA,"
                               " or Yosemite grading system"))
    parser.add_argument('-a','--area', type=str,
                        help=("Area, e.g. Frankenjura"))
    parser.add_argument('-s','--stars', type=int,
                        help=("Display routes with stars 0,1,2 or 3"))
    args = parser.parse_args()
    return args



def main():
    # Get command line arguments
    args = arguments()
    
    # Import the CSV file
    db=ClimbingQuery()
    if args.stars==None and args.area==None and args.grade==None:
        # I'm sure this if statement can be made nicer...
        print(db.getAllRoutes()) # ordered by grade!
    else:
        routes = db.getFilteredRoutes(area = args.area,
                                      stars= args.stars,
                                      grade= args.grade)
        print(routes)

    # db.get_crag_info("Wüstenstein")
    # db.give_os_F("9-","Frankenjura")
    # db.sort_by_date()

        
    ### DATABASE STUFF ###
    engine, metadata = connect2engine()
    session = createTablesStartSession(engine)
        
        

    ### PLOTTING (export to climbingQuery) ###
    # import plotly
    # import plotly.graph_objs as go
    # import matplotlib.pyplot as plt
    # from mpl_toolkits.mplot3d import Axes3D
    # Onsights, Flashs in different color
    # 3D plot: x=time, y=grade, z=number
    # from grade import French # Plots are in French grading
    # x = list(French.keys())
    # x.sort()
    # y = [len(list(filter(lambda x: x.grade.value==grade, routelist))) for grade in x]
    # data = [go.Bar(x=x,y=y)]
    # #plotly.offline.plot(data, auto_open=True)
    # #plt.bar(range(len(y)), y, align='center')
    # #plt.xticks(range(len(y)), x, size='small')
    # # setup the figure and axes
    # fig = plt.figure(figsize=(8, 3))
    # ax1 = fig.add_subplot(121, projection='3d')
    # bottom = 0
    # width = depth = 1
    # top = max(y)
    # ax1.bar3d(x, y, bottom, width, depth, top, shade=True)
    # ax1.set_title('Shaded')
    # plt.show()
    
    
if __name__ == "__main__":
    main()
        
