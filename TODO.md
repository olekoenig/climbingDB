Frontend:

- add achievements batch:
  - SANDBAGGER/GRADE INFLATOR
  - AMOUNT xsxOF METERS CLIMBED IN ONE DAY
  - ROUTE MARATHON, in X Gebieten
  - 8a boulder
  - Bleau parkour
  - Kommentator
- Google icon material design anstratt emojis
- stars -> visuell, 5 sterne statt 3
- cannot shift notes window when expanded
- zoom into plots
- Weltkarte mit Kletterorten
- add box to select if slash grades should be selectable
- add privacy for notes: in settings, can decide if one wants to show or not
- first time clicking on reset all filters creates: "The widget with key "stars_select" was created with a default value but also had its value set via the Session State API."
- profilbild
- make stars optional (later for mean)
- add route page
- share profile button
- display pitches of multipitch routes
- fix pitches_data in edit_routes
- pre-populate ALL info that is available if a route is selected
- Multipitches: Picture of wall uploadable, can mark the starting points/belays on the picture by clicking, put that into database
- routes over time
- "most successful days"
- integrate GPS, where to park, crag info

Backend:
- Bleau: parkour als MSL, mit Boulder grad
- Fix hack in get_filtered_routers with +0.5 for grade filtering (need to calculate distance properly)
- add 8a.nu import feature
- consensus grade = AVERAGE(ascent.grade), gewichtet mit #routen des users, evtl. mit erfahrung in diesem Grad?

Database:
- Add denormalized fields of area and crag in Route class for faster filtering/display
  crag_name = Column(String(200), index=True)
  remember to also sync:
  @validates('crag')
  def sync_location_names(self, key, crag_value):
- Clean up duplicate countries
- can a route have multiple grades depending on user? -> re-structure DB to allow multiple grades
