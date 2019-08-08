# from climbingQuery import ClimbingQuery

class Location:
    def __init__(self, crag, area, country, cragnote):
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


if __name__=="__main__":
    loc=Location(crag="On The Moon",country="Not Earth",
                 area="The Universe",cragnote="This is a test crag note")
    print(loc)
