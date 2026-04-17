Frontend:

- tabs instead of buttons for navigation
- add achievements batch:
  - climbed a worlds first (add FA dates)
  - climbed a Sharma route
  - "most successful days"
- stars -> visuell
- cannot shift notes window when expanded
- zoom into plots
- Weltkarte mit Kletterorten
- add box to select if slash grades should be selectable
- add privacy for notes: in settings, can decide if one wants to show or not
- first time clicking on reset all filters creates: "The widget with key "stars_select" was created with a default value but also had its value set via the Session State API."
- profilbild
- add route page
- share profile button
- display pitches of multipitch routes
- Multipitches: Picture of wall uploadable, can mark the starting points/belays on the picture by clicking, put that into database
- routes over time
- integrate GPS, where to park, crag info

Backend:
- Bleau: parkour als MSL, mit Boulder grad
- Fix hack in get_filtered_routers with +0.5 for grade filtering (need to calculate distance properly)
- consensus grade = AVERAGE(ascent.grade), gewichtet mit #routen des users, evtl. mit erfahrung in diesem Grad?

Database:
- Add denormalized fields of area and crag in Route class for faster filtering/display
  crag_name = Column(String(200), index=True)
  remember to also sync:
  @validates('crag')
  def sync_location_names(self, key, crag_value):
