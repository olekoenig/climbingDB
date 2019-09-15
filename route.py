from location import Location
from grade import Grade

class Route:
    def __init__(self, name, grade, style, crag, area, country,
                 shortnote, notes, date, project, stars, cragnote):

        # SHOULD MOVE CRAGNOTE INTO LOCATION! shouldn't be part of a
        # Route object

        # SHOULD CREATE NEW CLASS Ascent with fields:
        # route, grade, style, shortnote, notes, project, stars
        
        # name of the route
        self.name = name
        
        # grade can be given in UIAA, French and YDS scale
        # To be added: Elbsandstein scale
        # CHANGE: A route should actually NOT contain grade (some
        # people might find it easier/harder)
        self.grade = Grade(grade)

        # style can be: o.s., F, 2. Go, 3. Go, ...
        self.style = style

        # the crag is divided in Country, Area, Crag and can have a cragnote (string or NaN)
        self.location = Location(crag, area, country, cragnote)

        # shortnote can be: hard, soft, trad, clean, aid, AF, TR etc.
        self.shortnote = shortnote

        # note is a subjective description of the route
        self.notes = notes

        # date can have the format: Month Year, Day.Month.Year
        self.date = date

        # project can have "X" or NaN
        self.project = project

        # stars is a subjective description of the beauty of the route (0-3 stars)
        self.stars = stars

        
    def __repr__(self):
        # str(self.__dict__)
        return "{} \t {} \t {}".format(self.name, self.grade, self.location)

    def allInfo(self):
        return (("Name: {}\nGrade: {}\nStyle: {}\nLocation: {}\n"
                 "Notes: {}, {}\nDate: {}\nStars: {}").format(self.name, self.grade,
                  self.style, self.location,self.shortnote, self.notes,self.date, self.stars))
        
    def addRoute(self, name, grade, crag, area, country, notes):
        """
        This function should access the database "ROUTES", test
        whether the route is already recorded and then add it.
        The recorded fields should be: 
        name, grade, location (crag,area,country), notes
        Attention: This function is different from addAscent.
        """
        return False
    

if __name__=="__main__":
    route=Route(name="Schnubbeldibubb", grade="10a", style="On-sight",
                crag="On the Moon", area="The Universe",
                country="Not Earth", shortnote="hard", notes="Jippy",
                date="01-01-2100", project="X", stars="3",
                cragnote="This should be removed")
    print(route.allInfo())
