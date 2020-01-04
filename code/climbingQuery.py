from grade import Grade
# from route import Route
import pandas
import matplotlib.pyplot as plt
from math import isnan

class ClimbingQuery:
     """
     A class to perform queries in the climbing database.
     """

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
          data = pandas.read_csv("../data/routes.csv",
                                 sep=',', # csv file separated by comma
                                 header=0, # no header column
                                 parse_dates=["date"], # unify the dates
          )
          
          # Append a column ole_grade to pandas data frame
          data["ole_grade"]=data["grade"].apply(lambda x: Grade(x).conv_grade())

          return data
          
     
     def getFlashes(self, area=None, grade=None):
          """
          A function to return a route list of flashed routes in an area.
          :param grade: The grade, e.g. '7c' or '9' or '5.12d'
          :param area: Area name, e.g. "Frankenjura"
          """
          return self.getFilteredRoutes(grade=grade, area=area, style='F')

     
     def getOnsights(self, area=None, grade=None):
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
          # routes.hist(column="ole_grade",bins=30)
          # plt.show()

          fig, ax = plt.subplots(figsize=(20,10))
          grades=('4a','5a','6a','6b','6c','7a','7a+','7b','7b+',
                  '7c','7c+','8a','8a+','8b','8b+','8c')
          pos_x=[Grade(xx).conv_grade() for xx in grades]
          for ii in range(1,len(grades)-1,1):
               g=Grade(grades[ii]).conv_grade()
               gup=Grade(grades[ii+1]).conv_grade()
               glo=Grade(grades[ii-1]).conv_grade()
               ax.bar(g, len(routes[routes.ole_grade==g]))

          ax.set_xticks(pos_x)
          ax.set_xticklabels(grades)
          plt.show()
          return None

          
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
               if v and k=="stars":
                    routes = routes[routes[k] >= v] # to display all routes with stars>=value
               elif v:
                    routes = routes[routes[k] == v]
          return routes
                    

     def getCragInfo(self, cragname):
          """
          Prints the info about a crag.

          .. note:: To be changed to SQL query.
          """
          info=self.data[self.data.crag==cragname]
          if info.cragnote.any()==False:
               exit("No information about the route "+cragname+" available")
          else:
               return info.cragnote.all()
          
          
     def getRouteInfo(self,routename):
          """
          Get the logged information about a route.
          """
          info=self.data[self.data.name==routename]
          if info.notes.any()==False:
               exit("No information about the route "+routename+" available")
          else:
               return info.notes.all()
          

     def sort_by_date(self):
          # Sort the list by the date of the ascent
          # TO BE IMPLEMENTED
          return False
          
          # Sum up periods of one month
          # Add slash grades to upper grade


if __name__=="__main__":
     from climbingQuery import ClimbingQuery
                
     print("Testing class climbingQuery")
     db=ClimbingQuery()
     # print(db)
     print(db.getAllRoutes())

     print("\nPrint the crag info of Wüstenstein")
     print(db.getCragInfo("Wüstenstein"))
                
     print("\nPrint the route info of Odins Tafel")
     print(db.getRouteInfo("Odins Tafel"))

     # Print route numbers
     db.printRouteNumbers()

     # Print project list
     print(db.getProjects(area="Frankenjura"))

     print(db.getFilteredRoutes(area="Frankenjura",stars=2,grade="9-"))
     print(db.getOnsights(grade="9"))
     print(db.getFlashes(grade="8a"))