#!/usr/bin/env python3

from argparse import ArgumentParser
from argparse import RawTextHelpFormatter

import plotly
import plotly.graph_objs as go
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from climbingQuery import ClimbingQuery


def arguments():
    parser = ArgumentParser(description = ("Ole's climbing database"),
                             formatter_class=RawTextHelpFormatter)
    parser.add_argument('-g','--grade', type=str,
                         help=("Set grades to display in Frensh, UIAA,"
                               " or Yosemite grading system"))
    parser.add_argument('-a','--area', type=str,
                        help=("Area, e.g. Frankenjura"))
    parser.add_argument('-s','--stars', type=list,
                        help=("Display routes with stars >= value"))
    args = parser.parse_args()
    return args



def main():
     # Get command line arguments
     args = arguments()

     # Import the CSV file
     db=ClimbingQuery()
     routes = db.getFilteredRoutes(area = args.area,
                                   stars= args.stars,
                                   grade= args.grade)
     print(routes)

     # db.get_crag_info("Wüstenstein")
     # db.give_os_F("9-","Frankenjura")
     # db.sort_by_date()


     #To be plotted:
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
