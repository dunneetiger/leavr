import flask
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from app import app

def load_sqlite_to_df(sql="select * from tEmployee order by jDate"):
    sqlite_file = "app/db/leavr.db"
    conn = sqlite3.connect(sqlite_file)
    with conn:
        x = pd.read_sql(sql, conn)
    return x  

@app.route('/graphs')
def graphs():
    x = load_sqlite_to_df()
    x = x[pd.notnull(x['jDate'])]
    df = x[['jDate','country','id']]
    df = df.groupby(['jDate','country']).count().groupby(level=[1], as_index=False).cumsum()
    df = df.reset_index()
    fig = plt.figure(figsize=(12, 14))
    res = df.loc[df['country'] == "in"]
    res = res[['jDate', 'id']]
    res.set_index('jDate')
    fig, ax = plt.subplots()
    res['id'].plot(ax=ax ,figsize=(12, 10), title='test')
    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    # plt.xticks(res['jDate'], res.index.values )
    figfile.seek(0)
    data = base64.b64encode(figfile.getvalue())
    unique_countries = np.unique(x.country.ravel())
    # return flask.render_template("index.html", title='Graph', line_chart=res.to_html())
    return flask.render_template("graph.html", title='Graphs', graph=data)

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
