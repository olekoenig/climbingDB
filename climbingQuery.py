from grade import Grade
from route import Route
import pandas
import re
from dateutil import parser
import math as m

class ClimbingQuery:
     def __init__(self):
          (self.routelist,self.projectlist,self.data) = self._import_routes()

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
               if str(data.project[i])=="X":
                    projectlist.append(Route(*row.values))
               else:
                    routelist.append(Route(*row.values))

          # Append a column ole_grade to pandas data frame
          data["ole_grade"]=data["grade"].apply(lambda x: Grade(x).conv_grade())
          # print(data[data.ole_grade==Grade("8a+").conv_grade()][data.area=="Frankenjura"][data.project!="X"])
                    
          return routelist, projectlist, data

          
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
                    

     def getOnsightsFlashes(self, grade="7c", area="Frankenjura"):
          flashes =self.data[self.data.ole_grade==Grade(grade).conv_grade()][self.data.style=="F"]
          onsights=self.data[self.data.ole_grade==Grade(grade).conv_grade()][self.data.style=="o.s."]
          return flashes, onsights

     def printRouteNumbers(self):
          # print("smaller not working!")
          # print(f"Number of Routes <7a: {len(self._get_routes(grade='<7a')[0])}")
          print("Number of 7a-7a+'s: {}".format(len(self._get_routes(grade="7a")[0])+
                                                len(self._get_routes(grade="7a/7a+")[0])+
                                                len(self._get_routes(grade="7a+")[0])))
          print("Number of 7b-7b+'s: {}".format(len(self._get_routes(grade="7b")[0])))
          print("Number of 7c's: {}".format(len(self._get_routes(grade="7c")[0])))
          print("Number of 8a's: {}".format(len(self._get_routes(grade="8a")[0])))
          print("Number of 8a+'s: {}".format(len(self._get_routes(grade="8a+")[0])+len(self._get_routes(grade="8a/8a+")[0])))
          print("Number of 8b's: {}".format(len(self._get_routes(grade="8b")[0])+len(self._get_routes(grade="8a+/8b")[0])))
          print("Number of 8b+'s: {}".format(len(self._get_routes(grade="8b+")[0])+len(self._get_routes(grade="8b/8b+")[0])))
          print("Number of 8c's: {}".format(len(self._get_routes(grade="8c")[0])))


     def getAllRoutes(self):
          """
          Returns the complete route list.
          """
          return self.routelist
               
     def getProjects(self, area="all"):
          """
          Returns the complete project list.
          """
          projects = self.data[self.data.project=="X"]
          if area!="all":
               projects = projects[projects.area==area]
          return projects

          
     def _get_routes(self,grade="all",stars="all",areaname="all"):

          if areaname == "all":
               if grade != "all":
                    return self.getOnsightsFlashes(grade=grade,area="all")
               # else:
	       #      return self.routelist
               
          else:
               if grade=="all":
                    if stars=="all":
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
                
     print("\nNumber of on-sights and flashes in grade 9 in area Frankenjura")
     (chopped,os,F) = db.getOnsightsFlashes(grade="9",area="Frankenjura")
     print(os, "Onsights,", F, "Flashes (", os+F, ") out of",
           len(chopped), "(", int((os+F)/len(chopped)*100), "%)")

     print(", ".join([x.name for x in chopped])) # look up how to do separation by commas
                
     print("\nPrint route numbers")
     db.printRouteNumbers()

     print("Print project list")
     print(db.getProjects(area="Frankenjura"))
