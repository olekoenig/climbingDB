create table routes
(
NAME varchar,
GRADE varchar,
STYLE varchar,
CRAG_ID int,
SHORTNOTE varchar,
NOTES varchar,
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
