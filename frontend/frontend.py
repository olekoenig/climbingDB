from flask import Flask, render_template

app = Flask(__name__)

from climbingQuery import ClimbingQuery
db=ClimbingQuery()


import numpy as np

# // [{id=1, name="abc"},
# //  {id=2, name="abc"},
# //  {id=2, name="abc"}]

@app.route('/')
def index():
    routes=db.getFilteredRoutes(grade="8a",operation=">=")
    return render_template("index.html",routes=routes.to_html())


@app.route('/routes')
def routes():
    routes=db.getAllRoutes()
    return render_template("index.html",routes=routes.to_html())


@app.route('/routes/onsights/')
def routesonsights():
    routes=db.getOnsights()
    return render_template("index.html",routes=routes.to_html())

# @app.route('/routes/flashes/<int:grade>/<string:area>')
# def routesflashes(grade, area):
#     routes=db.getFlashes(area=area, grade=grade)
    

@app.route('/routes/flashes/<string:area>')
def routesflashes(area):
    routes=db.getFlashes(area=area)
    return render_template("index.html",routes=routes.to_html())

@app.route('/projects/<string:area>')
def projects(area):
    projects=db.getProjects(area=area)
    return render_template("index.html",routes=projects.to_html())

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
