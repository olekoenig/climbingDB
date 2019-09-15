from route import Route
from grade import Grade

class Ascent:

    def __init__(self, route, date,
                 grade=None, style=None, shortnote=None, notes=None, project=None, stars=None):
        """
        :param route: a route object
        :param date: date of the ascent (in format YYYY-MM-DD)
        :param grade: optional: a personal grade
        :param style: optional: None=red-point, o.s., F., 2.Go, 1day, etc.
        :param shortnote: optional: hard, soft, trad, R, X, clean, aid, AF, TR etc.
        :param notes: optional: subjective description of the route
        :param project: optional: to add a project set to "X"
        :param stars: optional: from 0,1,2 or 3
        """
        self.name = route.name
        self.grade = Grade(grade)
        self.style = style

        # the crag is divided in Country, Area, Crag and can have a cragnote (string or NaN)
        self.location = Location(route.location.crag,
                                 route.location.area,
                                 route.location.country,
                                 cragnote) # where from?

        self.shortnote = shortnote
        self.notes = notes
        self.date = date
        # project can have "X" or NaN
        self.project = project
        self.stars = stars

        
    def __repr__(self):
        return "{} \t {} \t {}\t {}".format(self.name, self.grade,
                                            self.style, self. shortnote)

    
    def addAscent(self, route, date, style=None, shortnote=None, stars=None, project=None):
        """
          This function should:
          1. Take a route object and go to ROUTES database
          2. If route is not in DB yet, call addRoute(route) in class Route
          3. add the ascent with the specified 
             * style: o.s. or F or NaN (default which means red-point)
             * shortnote: e.g. trad, soft, hard, R, X, 2.Go, 3.Go, 1day,...
             * date: should be a datetime object?
             * project
          .. todo:: Add personal grades
          """
        return False
    
    
    def addProject(self, route, shortnote=None, stars=None):
        """
          Adds a project to the database ASCENTS
          :param route: A Route object with name,grade,
          :
          :returns: addAscent with parameters
          addAscent in or
        """
        return self.addAscent(route=route, style=None,
                              shortnote=shortnote, date=None,
                              project="X", stars=stars)


if __name__=="__main__":
    ascent=Ascent(name="Schnubbeldibubb", grade="10a", style="On-sight",
                  crag="On the Moon", area="The Universe",
                  country="Not Earth", shortnote="hard", notes="Jippy",
                  date="01-01-2100", project="X", stars="3",
                  cragnote="This should be removed")
