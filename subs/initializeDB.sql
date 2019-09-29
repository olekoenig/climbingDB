create table LOCATIONS
(
CragID int NOT NULL,
PRIMARY KEY (CragID),

CRAG varchar, -- e.g. Waldkopf
AREA varchar, -- e.g. Frankenjura
COUNTRY varchar, -- e.g. Germany
CRAGNOTE varchar -- e.g. "Very cool overhang"
);

CREATE TABLE ROUTES
(
RouteID int NOT NULL, -- RouteID is primary key and unique
PRIMARY KEY (RouteID),
CragID int, -- CragID points to CragID in LOCATIONS DB
FOREIGN KEY (CragID) REFERENCES LOCATIONS(CragID),

NAME varchar, -- A non-unique name of a route
GRADE varchar, -- A route must have a proposed grade
NOTES varchar -- A string of notes which is extended further and futher
);

CREATE TABLE ASCENTS
(
AscentID int NOT NULL, -- not sure if AscentID is of use
PRIMARY KEY (AscentID), -- is a primary key obligatory?
RouteID int, -- RouteID is Foreign key and points to ROUTES DB
FOREIGN KEY (RouteID) REFERENCES ROUTES(RouteID),

GRADE varchar, -- Each route can have a personal grade
STYLE varchar, -- o.s., F., trad, etc.
SHORTNOTE varchar, -- hard, soft, 2. Go, etc.
DATE date, -- preferably in format YYYY-MM-DD
PROJECT char(1), -- either "X" if its a project or empty (NaN)
STARS int -- stars = 0, 1, 2, or 3
);

