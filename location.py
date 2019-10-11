# from climbingQuery import ClimbingQuery

class Location:
    def __init__(self, crag, area, country, cragnote=None):
        # for instance: Waldkopf
        self.crag = crag

        # for instance: Frankenjura
        self.area = area

        # for instance: Germany
        self.country = country

        # For instance: crag in the forest with the classic "Action Directe"
        self.cragnote = cragnote

        
    def __repr__(self):
        return "{} ({})".format(self.crag, self.area)


    def addCragnote(self, location, cragnote):
        """
        This function should:
        1. Query the SQL database "LOCATIONS"
        2. Add cragnote to string (string might be empty if no
           cragnote was added so far)
        3. Store in DB
        """
        return False
        

if __name__=="__main__":
    loc=Location(crag="On The Moon",
                 country="Not Earth",
                 area="The Universe",
                 cragnote="This is a test crag note")
    print(loc)
