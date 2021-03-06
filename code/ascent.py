from route import Route
from location import Location
from grade import Grade

# from sqlalchemy import MetaData, String, Column, Text, DateTime, Boolean, Integer, ForeignKey
# from sqlalchemy.ext.declarative import declarative_base
# from datetime import datetime
# Base = declarative_base() # not sure where Base belongs. Should it be
# # in the "deepest" file and then succesively loaded?

class Ascent():

    # __tablename__ = 'ASCENTS'
    
    # ascentID  = Column('ascentID', Integer, primary_key=True) # not sure AscentID can be of use
    # # How to implement Foreign Key???
    # # fkRouteID = Column('fkRouteID', Integer, ForeignKey("ROUTES.routeID")) # points to ROUTES table
    # grade     = Column('grade', String(10), nullable=True) # Each route can have a personal grade
    # style     = Column('style', String(10), nullable=True) # o.s., F., trad, etc.
    # shortnote = Column('shortnote', String(10), nullable=True) # hard, soft, 2. Go, etc.
    # date      = Column('date', DateTime, default=datetime.now)
    # project   = Column('project', Boolean, default=False)
    # stars     = Column('stars', Integer, nullable=True) # stars = 0, 1, 2, or 3

    # should launch connect_engine here?
    
    def __init__(self, route, date,
                 grade=None, style=None, shortnote=None, notes=None, project=None, stars=None):
        """
        :param route: a route object
        :param date: date of the ascent (in format YYYY-MM-DD)
        :param grade: optional: a personal grade
        :param style: optional: None=red-point, o.s., F., 2.Go, 1day, etc.
        :param shortnote: optional: hard, soft, trad, R, X, clean, aid, AF, TR etc.
        :param notes: optional: subjective description of the route
        :param project: optional: True or False
        :param stars: optional: from 0,1,2 or 3
        """
        self.name = route.name
        self.grade = Grade(grade)
        self.style = style

        # the crag is divided in Country, Area, Crag and can have a cragnote
        self.location = Location(route.location.crag,
                                 route.location.area,
                                 route.location.country,
                                 route.location.cragnote)

        self.shortnote = shortnote
        self.notes = notes
        self.date = date
        self.project = project # True of False
        self.stars = stars

        
    def __repr__(self):
        return "{} \t {} \t {}\t {}".format(self.name, self.grade,
                                            self.style, self. shortnote)

    
    # def addAscent(self, route, date, style=None, shortnote=None, stars=None, project=None):
    #     """
    #       This function should:
    #       1. Take a route object and go to ROUTES database
    #       2. If route is not in DB yet, call addRoute(route) in class Route
    #       3. add the ascent with the specified 
    #          * style: o.s. or F or NaN (default which means red-point)
    #          * shortnote: e.g. trad, soft, hard, R, X, 2.Go, 3.Go, 1day,...
    #          * date: should be a datetime object?
    #          * project
    #       """
    #     RouteID = getRouteID(route)
    #     return False

    
    # def getRouteID(self, route):
    #     """
    #     To add an entry into the table ASCENTS the RouteID is
    #     necessary. This function calls the table ROUTES for the RouteID.
    #     """
    #     return False
    
    
    # def addProject(self, route, shortnote=None, stars=None):
    #     """
    #       Adds a project to the table ASCENTS
    #       :param route: A Route object with name,grade,
    #       :
    #       :returns: addAscent with parameters
    #       addAscent in or
    #     """
    #     return self.addAscent(route=route, style=None,
    #                           shortnote=shortnote, date=None,
    #                           project="X", stars=stars)

    
    def allInfo(self):
        return (("Name: {}\nGrade: {}\nStyle: {}\nLocation: {}\n"
                 "Notes: {}, {}\nDate: {}\nStars: "
                 "{}").format(self.name, self.grade, self.style,
                             self.location, self.shortnote, self.notes,self.date,
                             self.stars))
    

    

if __name__=="__main__":
    ascent=Ascent( route = Route( name="Schnubbeldibubb",
                                  grade="8a",
                                  location= Location( crag="On the Moon",
                                                      area="The Universe",
                                                      country="Not Earth",
                                                      cragnote="coolest crag on the moon")),
                   date = "01-01-2100",
                   grade = "7c+",
                   style="o.s.",
                   shortnote="soft",
                   notes="soft because of low gravity",
                   project=False,
                   stars="3")

    print(ascent.allInfo())
