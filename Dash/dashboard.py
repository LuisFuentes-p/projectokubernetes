import dash
from dash import dcc, html
import pandas as pd
import psycopg2

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Commodity Transactions"),
    dcc.Interval(id="interval", interval=2000),  # every 2 sec
    dcc.Graph(id="graph")
])

@app.callback(
    dash.dependencies.Output("graph", "figure"),
    [dash.dependencies.Input("interval", "n_intervals")]
)
def update_graph(n):
    conn = psycopg2.connect(
        host="postgres",
        database="transactions_db",
        user="user",
        password="password"
    )
    df = pd.read_sql_query("SELECT * FROM transactions", conn)
    conn.close()

    if df.empty:
        return {}

    grouped = df.groupby("commodity")["total"].sum()

    return {
        "data": [{
            "x": grouped.index,
            "y": grouped.values,
            "type": "bar"
        }],
        "layout": {"title": "Total Value per Commodity"}
    }

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)