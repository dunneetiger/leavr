import flask
import sqlite3

from app import app

@app.route('/')
@app.route('/index')
@app.route('/WallOfHeroes')
def index():
    
    sqlite_file = "app/db/leavr.db"

    conn = sqlite3.connect(sqlite_file)

    employees = []
    with conn:

        conn.text_factory = str
        cur  = conn.cursor()
        # check if this is the first time the program is run
        for row in cur.execute('select uid, fname, title, jDate, lDate, country, team from tEmployee order by jDate;'):
            uid   = row[0]
            fname = row[1]
            title = row[2]
            jDate = row[3]
            lDate = row[4]
            if lDate or jDate == "0000-00-00" :
                active = False
            else:
                active = True
            country = row[5]
            team = row[6]

            employees.append({'uid': uid, 'fname': fname, 'title': title, 'active': active})

    
    return flask.render_template("index.html", title='Home', employees=employees)
