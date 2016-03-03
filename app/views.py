import flask
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


from app import app

def load_sqlite_to_df():
    sqlite_file = "app/db/leavr.db"
    conn = sqlite3.connect(sqlite_file)
    return pd.read_sql("select * from tEmployee order by jDate", conn)


@app.route('/leaver')
def leaver():
    x = load_sqlite_to_df()
    x = x[pd.notnull(x['lDate'])]
    x = x.sort(columns='lDate')
    return flask.render_template("index.html", title='Leavers', line_chart=x.to_html())

@app.route('/')
@app.route('/index')
@app.route('/WallOfHeroes')
def index():
   
    x = load_sqlite_to_df()
    return flask.render_template("index.html", title='Wall Of Heroes', line_chart=x.to_html())
