from grade import Grade
from route import Route
import pandas

class ClimbingQuery:
     def __init__(self):
          self.data = self._import_routes()

          
     def __str__(self):
          return self.getFilteredRoutes().sort_values(by=["ole_grade"]).__str__()


     def _import_routes(self):
          """
          Import the CSV file.
          :returns: data (Pandas data frame)
          
          .. note:: To be changed to SQL database.
          """
          # Import CSV file (should be changed to SQL query)
          data = pandas.read_csv("routes.csv",
                                 sep=',', # csv file separated by comma
                                 header=0, # no header column
                                 parse_dates=["date"], # unify the dates
          )
          
          # Append a column ole_grade to pandas data frame
          data["ole_grade"]=data["grade"].apply(lambda x: Grade(x).conv_grade())

          return data
          
     
     def getFlashes(self, grade=None, area=None):
          """
          A function to return a route list of flashed routes in an area.
          :param grade: The grade, e.g. '7c' or '9' or '5.12d'
          :param area: Area name, e.g. "Frankenjura"
          """
          return self.getFilteredRoutes(grade=grade, area=area, style='F')

     
     def getOnsights(self, grade=None, area=None):
          """
          A function to return a route list of onsighted routes in an area.
          :param grade: The grade, e.g. '7c' or '9' or '5.12d'
          :param area: Area name, e.g. "Frankenjura"
          """
          return self.getFilteredRoutes(grade=grade, area=area, style='o.s.')


     def printRouteNumbers(self):
          """
          Prints the number of routes in each grade and plots a histogram.
          """
          # Copy the data frame, otherwise it is overridden
          routes = self.data[self.data.project!="X"].copy()
          print("Number of Routes >= 8a: \t{}".format(len(routes[routes.ole_grade>=Grade("8a").conv_grade()])))
          print("Total number of routes: \t{}".format(len(routes)))
          # Plot the route distribution as matplotlib object (internal pandas function)
          routes.hist(column="ole_grade",bins=30)
          plt.show()

          
     def getAllRoutes(self, area=None):
          """
          Returns the complete route list in an area.
          """
          return self.getFilteredRoutes(area=area).sort_values(by=["ole_grade"]).__str__()

     
     def getProjects(self, area=None):
          """
          Returns the project list in an area.
          """
          projects = self.data[self.data.project=="X"]
          if area:
               projects = projects[projects.area==area]
          return projects

     
     def getFilteredRoutes(self, area=None, grade=None, style=None, stars=None):
          """
          Return a route list under the applied filters.
          :param area: Area name, e.g. 'Frankenjura'
          :param grade: Grade, e.g. '8a' or '9+/10-'
          :param style: Onsight 'o.s.' or Flash 'F'
          :param stars: Number of stars [0,1,2,3]
          :returns: pandas data frame
          """
          kwargs = {'area': area,
                    'ole_grade': Grade(grade).conv_grade(),
                    'style': style,
                    'stars': stars
          }

          # Copy the data frame, otherwise it is overridden
          routes = self.data[self.data.project!="X"].copy()

          # Go through the arguments and filter the list accordingly
          for k,v in kwargs.items():
               # if v and k=="stars":
               #      routes = routes[routes[k] >= v] # to display all routes with stars>=value
               if v:
                    routes = routes[routes[k] == v]
          return routes
                    

     def printCragInfo(self, cragname):
          """
          Prints the info about a crag.

          .. note:: To be changed to SQL query.
          """
          info=None
          for i, route in self.data.iterrows():
               if route.crag == cragname:
                    try:
                         m.isnan(route.cragnote)
                    except TypeError:
                         info=route.cragnote
                         break
          if info==None:
               print("No information about the crag", cragname, "available")
          else:
               print(info)
               return info

     def printRouteInfo(self,routename):
          info=None
          for route in self.routelist:
               if route.name==routename:
                    info=route.allInfo()
                    break
          if info==None:
               print("No information about the route", routename, "available")
          else:
               print(info)
               return info
          

     def sort_by_date(self):
          # Sort the list by the date of the ascent
          # TO BE IMPLEMENTED
          return 0
          
          # Sum up periods of one month
          # Add slash grades to upper grade


if __name__=="__main__":
     from climbingQuery import ClimbingQuery
                
     print("Testing class climbingQuery")
     db=ClimbingQuery()
     # print(db)
     # print(db.getAllRoutes())

     # print("\,Print the crag info of Wüstenstein")
     # db.printCragInfo("Wüstenstein")
                
     # print("\nPrint the route info of Odins Tafel")
     # db.printRouteInfo("Odins Tafel")
                                
     # Print route numbers
     db.printRouteNumbers()

     # Print project list
     # print(db.getProjects(area="Frankenjura"))

     # print(db.getFilteredRoutes(area="Frankenjura",stars=3))
     # print(db.getOnsights(area="Frankenjura",grade="9"))
