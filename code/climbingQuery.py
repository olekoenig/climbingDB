from grade import Grade, French

import pandas
import matplotlib.pyplot as plt


class ClimbingQuery:
     """
     A class to perform queries in the climbing database.
     """

     def __init__(self):
          self.data = self._import_routes()

          
     def __str__(self):
          return self.getFilteredRoutes().sort_values(by=["ole_grade"]).__str__()


     def _import_routes(self):
          """Import the CSV file.

          .. note:: To be changed to SQL database.

          :returns: data (Pandas data frame)
          """

          # Import CSV file (should be changed to SQL query) ###########################################################
          # Read in sport climbing routes
          df = pandas.read_csv("../data/routes.csv",
                                 sep=',', # csv file separated by comma
                                 header=0, # no header column
                                 parse_dates=["date"], # unify the dates
                                 )

          # Read in multipitch routes
          df_multipitches = pandas.read_csv("../data/multipitches.csv",sep=',',header=0,parse_dates=["date"])

          # Merge the two dataframe
          df=df.append(df_multipitches, sort=True)

          # Append a column ole_grade to pandas data frame
          df["ole_grade"]=df["grade"].apply(lambda x: Grade(x).conv_grade())

          # Set the NaN values to "" or 0
          df['stars']=df['stars'].fillna(0)
          df['style']=df['style'].astype(object).fillna("")
          df['shortnote'] = df['shortnote'].astype(object).fillna("")
          df['notes'] = df['notes'].astype(object).fillna("")

          return df


     def printRouteNumbers(self):
          """Prints the number of routes in each grade and plots a histogram."""
          # Copy the data frame, otherwise it is overridden
          routes = self.data[self.data.project!="X"].copy()
          print("Number of Routes >= 8a: \t{}".format(len(routes[routes.ole_grade>=Grade("8a").conv_grade()])))
          print("Total number of routes: \t{}".format(len(routes)))

          # Plot the route distribution with internal pandas function
          # routes.hist(column="ole_grade",bins=30) ; plt.show()
          # Plot all grades (also slash grades)
          x = list(French.keys()) #.sort()
          y = [len(routes[routes.ole_grade==Grade(grade).conv_grade()]) for grade in x]
          plt.bar(x,y) ; plt.show()

          # Plot route distribution
          # Need to account for the slash grades, so one cannot only
          # plot the grades of, e.g., 8a, 8a+ etc. but has to get also
          # the routes grated 8a/8a+.
          # A route gradet 8a/8a+ belongs to the 8a bar.
          fig, ax = plt.subplots(figsize=(20,10))
          grades=('4a','5a','6a','6b','6c','7a','7a+','7b','7b+',
                  '7c','7c+','8a','8a+','8b','8b+','8c')
          pos_x=[Grade(xx).conv_grade() for xx in grades]
          for ii in range(1,len(grades)-1,1):
               g=Grade(grades[ii]).conv_grade()
               gup=Grade(grades[ii+1]).conv_grade()
               # Get all routes >= 8a
               len_glo=len(routes[routes.ole_grade>=g])
               # Get all routes >=8a+
               len_gup=len(routes[routes.ole_grade>=gup])
               # Number of routes is set of len_glo AND len_gup
               len_tot=len_glo-len_gup
               ax.bar(g, len_tot, color="blue")
          ax.set_xticks(pos_x)
          ax.set_xticklabels(grades)
          plt.show()

          
     def getMultipitches(self):
          mp = self.data[self.data['pitches'].notna()]
          return mp.sort_values(by = ["ole_grade"])

     
     def getProjects(self, crag = None, area = None):
          """Returns the project list in a crag or area."""

          projects = self.data[self.data.project == "X"]
          
          if area:
               projects = projects[projects.area == area]
          if crag:
               projects = projects[projects.crag == crag]

          return projects.sort_values(by=["ole_grade"])

     
     def getFilteredRoutes(self, crag=None, area=None, grade=None, style=None,
                           stars=None, operation="=="):
          """
          Return a route list under the applied filters.

          :param crag: Crag name, e.g. 'Schlaraffenland'
          :param area: Area name, e.g. 'Frankenjura'
          :param grade: Grade, e.g. '8a' or '9+/10-'
          :param style: Onsight 'o.s.' or Flash 'F'
          :param stars: Number of stars [0,1,2,3]
          :param operation: logic operation applied to grade [default: ==], currently supported: ==,>=
          :returns: pandas data frame
          """
          kwargs = {'crag': crag,
                    'area': area,
                    'ole_grade': Grade(grade).conv_grade(),
                    'style': style,
                    'stars': stars
          }

          # Copy the data frame, otherwise it is overridden
          routes = self.data[self.data.project!="X"].copy()
          
          # Go through the arguments and filter the list accordingly
          for k,v in kwargs.items():
               
               if v and k=="stars" or (k=="ole_grade" and operation==">="):
                    # applies if stars set: display routes with stars>=value
                    # or applies if operation is larger-equal and grade set
                    routes = routes[routes[k] >= v]

               elif v and k=="ole_grade":
                    # HACK: try to display, e.g., also 9/9+ routes if grade=9
                    routes = routes[(routes[k] == v) | (routes[k] == v+0.5)]
                    
               elif v:
                    routes = routes[routes[k] == v]
                    
          return routes.sort_values(by=["ole_grade"])
     
     
     def getCragInfo(self, cragname):
          """Prints the info about a crag.

          .. note:: To be changed to SQL query.
          """
          info=self.data[self.data.crag==cragname]
          if info.cragnote.any()==False:
               print("No information about the route "+cragname+" available")
          else:
               print(info.cragnote.all())
          
          
     def getRouteInfo(self,routename):
          """Get the logged information about a route."""
          info=self.data[self.data.name==routename]
          if info.notes.any()==False:
               print("No information about the route "+routename+" available")
          else:
               print(info.notes.all())
          

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

     # print("\nPrint the crag info of Wüstenstein")
     # print(db.getCragInfo("Wüstenstein"))
                
     # print("\nPrint the route info of Odins Tafel")
     # print(db.getRouteInfo("Odins Tafel"))

     # Print route numbers
     # db.printRouteNumbers()

     # Print project list
     # print(db.getProjects(area="Frankenjura"))

     print(db.getFilteredRoutes(area="Frankenjura",stars=2,grade="8a+",operation=">="))
