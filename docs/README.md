# ToDo to build the documentation:

See also: https://www.sphinx-doc.org/en/master/usage/quickstart.html

* ```apt-get install python3-sphinx``` and run ```sphinx-quickstart``` 
* Install ```sphinx_rtd_theme``` with ```sudo python3 -m pip install sphinx_rtd_theme```
* Uncomment the ```sys.path.insert(0, os.path.abspath('.'))``` line
  and add path to the code
* Add ```'sphinx.ext.autodoc'``` to the extensions in ```conf.py```
* Go into **source/** and add scripts to table of contents, e.g. ```scripts/climbingQuery.rst```
* Create .rst file for each script with, e.g.,

```
climbingQuery.py
================

.. automodule:: climbingQuery
   :members:

.. autoclass:: ClimbingQuery
   :members:
   :private-members:
```

* Do ```make html``` in **docs/**
* Do ```firefox build/html/index.html```
