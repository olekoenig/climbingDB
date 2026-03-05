Frontend:

- PAUL: stars -> visuell, 5 sterne statt 3
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
- Fix hack in get_filtered_routers with +0.5 for grade filtering (need to calculate distance properly)
- add 8a.nu import feature

Database:
- Clean up duplicate countries
- can a route have multiple grades depending on user? -> re-structure DB to allow multiple grades
