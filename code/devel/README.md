# Ole's Awesome Climbing Database

* python3 wrapper for SQL query: ```sqlalchemy```


### Useful SQL commands:

* Create database

```sql
sudo -i -u postgres
psql
CREATE DATABASE DatabaseName\g
```

* Add data into database
```\copy TableName from datatable.txt using delimiters '|'```

* Access to database:
```psql DatabaseName```

* See what is in the table
```sql
\d
select * from exosat_images
```

* Log in as postgresql superuser
```sudo -i -u postgres```

* Load script into database
```psql name < script.txt```

* Delete entries from database
```truncate name;```
