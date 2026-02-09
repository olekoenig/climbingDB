from area import Area
import config

class Crag(Area):
    def __init__(self, crag, area, country,
                 gps_crag = None, gps_parking = None, cragnote = None):
        super().__init__(area, country) 
        self.crag = crag
        self.gps_crag = gps_crag
        self.gps_parking = gps_parking
        
    def __repr__(self):
        return "{} ({}, {})".format(self.crag, self.area, self.country)

    
if __name__=="__main__":
    loc = Crag(crag = "Crate III",
               country = "Moon",
               area = "The Universe",
               cragnote = "The coolest extraterrestrial climbing crag!")
    print(loc)
        
