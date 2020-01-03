#!/usr/bin/env python3

"""
main can be used directly from the command line to query the database
see ./main.py --help
"""

from argparse import ArgumentParser
from argparse import RawTextHelpFormatter

# from sqlalchemy.orm import sessionmaker
# from sqlalchemy import create_engine
# from sqlalchemy import MetaData
# from ascent import Ascent, Base

from climbingQuery import ClimbingQuery # Get query functions


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
    parser.add_argument('--style', type=str,
                        help=("e.g. o.s., F., 2. Go, 1 day"))
    parser.add_argument('--getFlashes', action='store_true')
    parser.add_argument('--getOnsights', action='store_true')
    parser.add_argument('--printRouteNumbers', action='store_true')
    parser.add_argument('--getAllRoutes', action='store_true')
    parser.add_argument('--getProjects', action='store_true')
    parser.add_argument('--getCragInfo', type=str)
    parser.add_argument('--getRouteInfo', type=str)
    args = parser.parse_args()
    return args


# def connect2engine():
#     """
#     Connecting to PostgreSQL server at localhost using psycopg2 DBAPI
#     Syntax: <username>:<password>@<host>/<dbname>
#     Engine object is how to interact with database

#     .. note:: Passwort of postgres changed from sudo pw to a new one with "\password postgres"

#     :returns: engine, metadata
#     """
#     engine=create_engine("postgresql+psycopg2://postgres:climbingdbPW!@localhost/sandbox")
#     engine.connect()
#     # print(engine)
#     metadata = MetaData()
#     return engine, metadata


# def createTablesStartSession(engine):
#     Base.metadata.create_all(engine, checkfirst=True)
#     Session = sessionmaker(bind=engine)
#     session = Session()
#     return session




def main():
    # Get command line arguments
    args = arguments()
    
    # Import the CSV file
    db=ClimbingQuery()

    # Test for the different arguments
    if args==None or args.getAllRoutes:
        routes=db.getAllRoutes(area=args.area) # print routes ordered by grade
    elif args.getFlashes:
        routes=db.getFlashes(area=args.area,grade=args.grade)
    elif args.getOnsights:
        routes=db.getOnsights(area=args.area,grade=args.grade)
    elif args.printRouteNumbers:
        routes=db.printRouteNumbers()
    elif args.getProjects:
        routes=db.getProjects(area=args.area)
    elif args.getCragInfo:
        routes=db.getCragInfo(args.getCragInfo)
    elif args.getRouteInfo:
        routes=db.getRouteInfo(args.getRouteInfo)
    else:
        routes = db.getFilteredRoutes(area = args.area,
                                      stars= args.stars,
                                      grade= args.grade,
                                      style= args.style)
    print(routes)

        
    ### DATABASE STUFF ###
    # engine, metadata = connect2engine()
    # session = createTablesStartSession(engine)
        
        

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
        
