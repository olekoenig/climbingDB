create table routes
(
NAME varchar,
GRADE varchar,
CRAG_ID int, ??? NECESSARY ???
NOTES varchar,
)

create table ascent
(
ROUTE_ID int, ??? NECESSARY ???
STYLE varchar,
SHORTNOTE varchar,
DATE date,
PROJECT char(1),
STARS int
)

create table locations
(
CRAG_ID int,
CRAG varchar,
AREA varchar,
COUNTRY varchar,
CRAGNOTE varchar
)
