import plotly_express as px
import plotly.graph_objects as go


def plot_trace_line(df, pollutant="nox", zoom=16, height=500):
    df = df.loc[:, df.columns != 'timestamp']
    center = df.mean()

    fig = px.line_mapbox(df, lat="lat", lon="lon", zoom=3, height=height)
    fig.update_layout(
            mapbox_style="open-street-map", mapbox_zoom=zoom,
            mapbox_center_lat=center.lat, mapbox_center_lon=center.lon,
            margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig.show()


def plot_trace(df, pollutant="nox", zoom=16, height=500):
    df = df.loc[:, df.columns != 'timestamp']
    center = df.mean()
    fig = go.Figure(
            go.Densitymapbox(
                lat=df.lat, lon=df.lon, z=df[pollutant], radius=10))
    fig.update_layout(
            mapbox_style="open-street-map", mapbox_zoom=zoom,
            mapbox_center_lat=center.lat, mapbox_center_lon=center.lon,
            margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig.show()


def plot_line(df, x, y, title=""):
    df = df.loc[:, df.columns != 'timestamp']
    fig = px.line(df, x=x, y=y, title=title)
    fig.show()
