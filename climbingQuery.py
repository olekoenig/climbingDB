from grade import Grade
from route import Route
import pandas
import re
from dateutil import parser
import math as m

class ClimbingQuery:
     def __init__(self):
          (self.routelist,self.projectlist) = self._import_routes()

     def __repr__(self):
          self.display(grade="all",stars="all",areaname="all")
          
     def _import_routes(self):
          data = pandas.read_csv("routes.csv", sep=',', header=0)
          routelist = []; projectlist = []
          for i, row in data.iterrows():          
               # Unify dates
               try:
                    row.date = parser.parse(str(data.date[i]))
               except ValueError:
                    if str(data.project[i]) != "X":
                         print("The climb", data.name[i],
                               "is no project but has no date! "+
                               "Setting date to 2000-12-31")
                         row.date = parser.parse("2000-12-31")
                    else:
                         pass
          
               # Sort climbed routes and projects
               if str(data.project[i]) == "X":
                    projectlist.append(Route(*row.values))
               else:
                    routelist.append(Route(*row.values))
                    
          return routelist, projectlist

          
     # Display routes in lines, sorted by grades
     # To be implemented: Highlight Onsights and Flashes in the List
     def display(self,grade,stars,areaname):
          # Get the routes
          routes=self._get_routes(grade,stars,areaname)

          # sort the list by grades
          routes.sort(key=lambda x: x.grade.conv_grade())
          
          for route in routes:
               # if line.style == "o.s.":
               #      print(line+"(on-sight)")
               # elif line.style == "F":
               #      print(line+"(flash)")
               # else:
               print(route)
                    

     def getOnsightsFlashes(self,grade, areaname):
          os = 0; F = 0
          if areaname == "all":
               chopped = list(filter(lambda x:x.grade.conv_grade()==Grade(grade).conv_grade(),
                                     self.routelist))
          else:
               # Find number of Onsights and Flashes in this grade
               chopped = list(filter(lambda x:x.grade.conv_grade()==Grade(grade).conv_grade() and
                                     x.location.area==areaname, self.routelist))
          
          for line in chopped:
               if line.style == "o.s.":
                    os += 1
               elif line.style == "F":
                    F += 1

          print("Number of on-sights and flashes in grade",grade,"in area",areaname)
          print(os, "Onsights,", F, "Flashes (", os+F, ") out of",
                len(chopped), "(", int((os+F)/len(chopped)*100), "%)")
          
          return chopped


     def _get_routes(self,grade, stars, areaname):
          if areaname == "all":
               if grade != "all":
                    return self.getOnsightsFlashes(grade,"all")
               else:
                    return self.routelist
     
          else:
               if grade == "all":
                    if stars == "all":
                         return list(filter(lambda x: x.location.area==areaname, self.routelist))
                    else:
                         return list(filter(lambda x: x.stars in stars
                                            and x.location.area==areaname, self.routelist))
     
               
               else:
                    #getOnsightsFlashes(grade,areaname)
                    if stars == "all":
                         return list(filter(lambda x:
                                            x.grade.conv_grade()==Grade(grade).conv_grade() and
                                            x.location.area==areaname, self.routelist))
               
                    else:
                         return list(filter(lambda x:
                                            x.grade.conv_grade()==Grade(grade).conv_grade()
                                            and x.stars in stars and
                                            x.location.area==areaname, self.routelist))
               
               

     def printCragInfo(self,cragname):
          info=None
          for route in self.routelist:
               if route.location.crag == cragname:
                    try:
                         m.isnan(route.location.cragnote)
                    except TypeError:
                         info=route.location.cragnote
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
          # TO BE IMPLEMENTED. something like:
          self.routelist.sort(key=lambda x: x.date)
          
          # Sum up periods of one month
          # Add slash grades to upper grade


if __name__=="__main__":
    from climbingQuery import ClimbingQuery

    print("Testing class climbingQuery")
    db=ClimbingQuery()
    # print(db)

    print("Display all routes in grade 9+ with 2-3 stars in Franken")
    db.display("5.13a",[2,3],"Frankenjura")

    print("\,Print the crag info of Wüstenstein")
    db.printCragInfo("Wüstenstein")

    print("\nPrint the route info of Odins Tafel")
    db.printRouteInfo("Odins Tafel")

    print("") # linebreak
    routes=db.getOnsightsFlashes("9","Frankenjura")
    print(*[x.name for x in routes]) # look up how to do separation by commas
