from .grade import Grade
from .config import *

import pandas as pd


class ClimbingQuery:
     """
     A class to perform queries in the climbing database.
     """

     def __init__(self):
          self.data = self._import_routes()

     def __str__(self):
          df = self.get_filtered_routes()[['name','grade','style','crag','shortnote','notes','date','stars']]
          return df.__str__()

     def _import_routes(self):
          """Import the CSV file.

          .. note:: To be changed to SQL database.

          :returns: data (Pandas data frame)
          """

          df_sport = pd.read_csv(ROUTES_CSV_FILE, sep = ';', header = 0, encoding = 'utf-8',
                                 parse_dates = ["date"], keep_default_na = False)
          df_boulders = pd.read_csv(BOULDERS_CSV_FILE, sep = ';', header = 0, encoding = 'utf-8',
                                    parse_dates = ["date"], keep_default_na = False)
          df_multipitches = pd.read_csv(MULTIPITCHES_CSV_FILE, sep = ';', header = 0, encoding = 'utf-8',
                                        parse_dates = ["date"], keep_default_na = False)

          df_sport["discipline"] = "Sportclimb"

          df_boulders["discipline"] = "Boulder"

          df_multipitches["discipline"] = "Multipitch"
          self._convert_multipitch_pitches(df_multipitches)

          df = pd.concat([df_sport, df_multipitches, df_boulders], sort = True)

          df["ole_grade"] = df["grade"].apply(lambda x: Grade(x).conv_grade())

          # Fix boulders which have YDS/UIAA grades (usually very easy, setting to V0 equivalent)
          boulder_mask = df["discipline"] == "Boulder"
          wrong_scale_mask = df["grade"].apply(lambda g: Grade(g).get_scale() in ['YDS', 'UIAA'])
          df.loc[boulder_mask & wrong_scale_mask, "ole_grade"] = 0

          # Convert stars column to float and set empty cells to zero
          df['stars'] = df['stars'].where(df['stars'] != "", other = 0).astype(float)

          return df

     def _convert_multipitch_pitches(self, df):
          """Convert the column "pitches" into numerical ole_grade."""
          pitches_ole_grades = []
          for index, row in df.iterrows():
               if row.pitches != "":
                    pitches = row.pitches.split(",")
                    pitches_ole_grades.append(list(Grade(pitch.strip("()")).conv_grade() for pitch in pitches))
               else:
                    # If no information on pitches is available, insert total grade
                    pitches_ole_grades.append([Grade(row.grade).conv_grade()])
          
          df["pitches_ole_grade"] = pitches_ole_grades
          
     def get_multipitches(self):
          df = self.data[self.data['discipline'] == "Multipitch"]
          return df.sort_values(by = ["ole_grade"])

     def get_boulders(self):
          df = self.data[self.data['discipline'] == "Boulder"]
          return df.sort_values(by = ["ole_grade"])
     
     def get_projects(self, crag = None, area = None):
          """Returns the project list in a crag or area."""

          projects = self.data[self.data.project == "X"]
          
          if area:
               projects = projects[projects.area == area]
          if crag:
               projects = projects[projects.crag == crag]

          return projects.sort_values(by=["ole_grade"])

     def get_filtered_routes(self, discipline="Sportclimb",
                             crag=None, area=None, grade=None, style=None,
                             stars=None, operation="=="):
          """
          Return a route list under the applied filters.

          :param discipline: Sportclimb, Boulder, or Multipitch"
          :param crag: Crag name, e.g. 'Schlaraffenland'
          :param area: Area name, e.g. 'Frankenjura'
          :param grade: Grade, e.g. '8a' or '9+/10-'
          :param style: Onsight 'o.s.' or Flash 'F'
          :param stars: Number of stars [0,1,2,3]
          :param operation: logic operation applied to grade [default: ==], currently supported: ==,>=
          :returns: pandas data frame
          """
          kwargs = {'discipline': discipline,
                    'crag': crag,
                    'area': area,
                    'ole_grade': Grade(grade).conv_grade(),
                    'style': style,
                    'stars': stars
          }

          # De-select projects, copy the data frame, otherwise it is overridden
          routes = self.data[self.data.project != "X"].copy()
          
          for k,v in kwargs.items():
               if v and k=="stars" or (k=="ole_grade" and operation==">="):
                    # applies if stars set: display routes with stars >= value
                    # or applies if operation is larger-equal and grade set
                    routes = routes[routes[k] >= v]
               elif v and k=="ole_grade":
                    # HACK: try to display, e.g., also 9/9+ routes if grade=9
                    routes = routes[(routes[k] == v) | (routes[k] == v+0.5)]
               elif v:
                    routes = routes[routes[k] == v]
                    
          return routes.sort_values(by=["ole_grade"])     
     
     def get_crag_info(self, cragname):
          """Prints the info about a crag.

          .. note:: To be changed to SQL query/store this info somewhere else
          """
          info=self.data[self.data.crag==cragname]
          if info.cragnote.any()==False:
               print("No information about the route "+cragname+" available")
          else:
               print(info.cragnote.all())
          
     def get_route_info(self,routename):
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
     print("Testing class climbingQuery")
     db = ClimbingQuery()

     boulders = db.get_boulders()
     print(boulders[['name','grade','style','crag','shortnote','notes','date','stars']])
     
     # print("\nPrint the crag info of Wüstenstein")
     # print(db.get_crag_info("Wüstenstein"))
                
     # print("\nPrint the route info of Odins Tafel")
     # print(db.get_route_info("Odins Tafel"))

     # db.print_route_numbers()

     # print(db.get_projects(area="Frankenjura"))

     #print(db.get_filtered_routes(discipline="Boulder", area="Frankenjura"))
     #print(db.get_filtered_routes(discipline="Sportclimb", area="Frankenjura",stars=2,grade="7a",operation=">="))

     
