from location import Location
from grade import Grade

class Route:

    def __init__(self, name, grade, location, notes=None):
        # name of the route
        self.name = name
        
        # grade can be given in UIAA, French and YDS scale
        # To be added: Elbsandstein scale
        self.grade = Grade(grade) # proposed grade

        # the crag is divided in Country, Area, Crag and can have a cragnote
        self.location = location # a Location object

        # note is a subjective description of the route
        self.notes = notes
        
        
    def __repr__(self):
        # str(self.__dict__)
        return "{} \t {} \t {}".format(self.name, self.grade, self.location)

    
    def addRoute(self, name, grade, crag, area, country, notes):
        """
        This function should access the database "ROUTES", test
        whether the route is already recorded and then add it.
        The recorded fields should be: 
        name, grade, location (crag,area,country), notes
        Attention: This function is different from addAscent.
        """
        return False

    def getPrimaryCragKey(self, name):
        """
        I think this function is necessary to insert a route into the
        database. One has to get the CragID to get the reference to
        LOCATIONS correctly.
        """
        return False
                           
    

if __name__=="__main__":
    route=Route(name="Schnubbeldibubb",
                grade="8a",
                location=Location( crag="On the Moon",
                                   area="The Universe",
                                   country="Not Earth" ),
                notes="First route on the moon")
    
    print(route)
