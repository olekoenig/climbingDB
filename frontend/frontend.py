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
    routes=db.getOnsights(area="Frankenjura",grade="9")
    return render_template("index.html",boulders=routes.to_html())


@app.route('/boulders')
def boulders():
    routes=db.getAllRoutes()
    return render_template("index.html",boulders=routes.to_html())


@app.route('/boulders/onsights/')
def bouldersonsights():
    routes=db.getOnsights(area="Frankenjura")
    return render_template("index.html",boulders=routes.to_html())

# @app.route('/boulders/flashes/<int:grade>/<string:area>')
# def bouldersflashes(grade, area):
#     routes=db.getFlashes(area=area, grade=grade)
    

@app.route('/boulders/flashes/<string:area>')
def bouldersflashes(area):
    routes=db.getFlashes(area=area)
    return render_template("index.html",boulders=routes.to_html())

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
