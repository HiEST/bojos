import pandas as pd
import pandas.io.sql as sqlio
import psycopg2
import plotly_express as px

import plotly.graph_objects as go


def plot_trace_line(df, pollutant = "nox", zoom = 16, height = 500):
    center = df.mean()
    color = pd.qcut(df[pollutant], 4, duplicates='drop')
    
    fig = px.line_mapbox(df, lat="lat", lon="lon", zoom=3, height=height)
    fig.update_layout(mapbox_style="stamen-terrain", mapbox_zoom=zoom, mapbox_center_lat = center.lat, mapbox_center_lon = center.lon,
        margin={"r":0,"t":0,"l":0,"b":0})

    fig.show()

def plot_trace(df, pollutant = "nox", zoom = 16, height = 500):
    center = df.mean()
    fig = go.Figure(go.Densitymapbox(lat=df.lat, lon=df.lon, z=df[pollutant], radius=10))
    fig.update_layout(mapbox_style="stamen-terrain", mapbox_zoom=zoom, mapbox_center_lat = center.lat, mapbox_center_lon = center.lon,
        margin={"r":0,"t":0,"l":0,"b":0})
    fig.show()


def plot_line(df, x, y, title=""):
    fig = px.line(df, x=x, y=y, title=title)
    fig.show()


def get_data(username, sid, joint=True):
    conn = psycopg2.connect(
        "dbname='bojos' user='bojos' host='sto02' password='dame_datos' port='5430'")

    # With pandas
    if joint:
        sql = "SELECT ts, ST_X(geom::geometry) AS lon, ST_Y(geom::geometry) AS lat, " + \
                "noxme+noxae as nox, soxme+soxae as sox, co2me+co2ae as co2, come+coae as co" + \
                " FROM locations WHERE sid = " + str(sid) + \
                " AND uid = (SELECT uid FROM users WHERE username = \'"+ username +"\' );"
    else:
        sql = "SELECT ts, ST_X(geom::geometry) AS lon, ST_Y(geom::geometry) AS lat, " + \
        "noxme, noxae, soxme, soxae, co2me, co2ae, come, coae, speed, pme, pae" + \
        " FROM locations WHERE sid = " + str(sid) + \
        " AND uid = (SELECT uid FROM users WHERE username = \'"+ username +"\' );"
    df = sqlio.read_sql_query(sql, conn)
    conn.close()
    return(df)

def get_summary(username):
    conn = psycopg2.connect(
        "dbname='bojos' user='bojos' host='sto02' password='dame_datos' port='5430'")

    # With pandas
    sql = "SELECT sid as slot, SUM(noxme) as NOxME, SUM(noxae) as NOxAE, SUM(soxme) as SOxME, SUM(soxae) as SOxAE, SUM(co2me) as CO2ME, SUM(co2ae) as CO2AE, SUM(come) as COME, SUM(coae) as COAE" + \
            " FROM locations WHERE " + \
            " uid = (SELECT uid FROM users WHERE username = \'"+ username +"\' )" + \
            " GROUP BY sid;"
    df = sqlio.read_sql_query(sql, conn)
    conn.close()
    return(df)

