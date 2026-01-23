class Area:
    def __init__(self, area, country, areanote = None):
        self.area = area
        self.country = country
        self.areanote = areanote
        
    def __repr__(self):
        return "{} ({})".format(self.area, self.country)

    
if __name__=="__main__":
    loc = Area(country = "Not Earth",
               area = "The Universe",
               areanote = "The coolest extraterrestrial climbing area!")
    print(loc)
