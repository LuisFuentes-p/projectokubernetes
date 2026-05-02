import dash
from dash import dcc, html
import pandas as pd
import psycopg2

app = dash.Dash(__name__)


def build_table(headers, rows):
    return html.Table(
        [
            html.Thead(html.Tr([html.Th(header) for header in headers])),
            html.Tbody([
                html.Tr([html.Td(cell) for cell in row])
                for row in rows
            ])
        ],
        style={"width": "100%", "borderCollapse": "collapse", "marginTop": "16px"}
    )

app.layout = html.Div([
    html.H1("Commodity Transactions"),
    dcc.Interval(id="interval", interval=2000),  # every 2 sec
    html.Div(id="summary"),
    dcc.Graph(id="price_line_graph"),
    dcc.Graph(id="quantity_graph")
])

@app.callback(
    dash.dependencies.Output("price_line_graph", "figure"),
    [dash.dependencies.Input("interval", "n_intervals")]
)
def update_price_line_chart(n):
    conn = psycopg2.connect(
        host="postgres",
        database="transactions_db",
        user="user",
        password="password"
    )
    transactions = pd.read_sql_query(
        """
        SELECT timestamp, commodity, price
        FROM transactions
        WHERE timestamp >= NOW() - INTERVAL '5 minutes'
        ORDER BY timestamp
        """,
        conn
    )
    conn.close()

    if transactions.empty:
        return {"data": [], "layout": {"title": "No price history available in last 5 minutes"}}

    traces = []
    for commodity, group in transactions.groupby("commodity"):
        ordered = group.sort_values("timestamp")
        traces.append({
            "x": ordered["timestamp"],
            "y": ordered["price"],
            "name": commodity,
            "type": "scatter",
            "mode": "lines+markers"
        })

    return {
        "data": traces,
        "layout": {
            "title": "Commodity Price Over Time (Last 5 Minutes)",
            "xaxis": {"title": "Timestamp"},
            "yaxis": {"title": "Price"}
        }
    }


@app.callback(
    dash.dependencies.Output("quantity_graph", "figure"),
    [dash.dependencies.Input("interval", "n_intervals")]
)
def update_quantity_chart(n):
    conn = psycopg2.connect(
        host="postgres",
        database="transactions_db",
        user="user",
        password="password"
    )
    transactions = pd.read_sql_query(
        """
        SELECT timestamp, commodity, quantity
        FROM transactions
        WHERE timestamp >= NOW() - INTERVAL '5 minutes'
        """,
        conn
    )
    conn.close()

    if transactions.empty:
        return {"data": [], "layout": {"title": "No quantity data available in last 5 minutes"}}

    quantity_by_commodity = transactions.groupby("commodity", as_index=False)["quantity"].sum()
    quantity_by_commodity = quantity_by_commodity.sort_values("commodity")

    return {
        "data": [{
            "x": quantity_by_commodity["commodity"],
            "y": quantity_by_commodity["quantity"],
            "name": "Quantity",
            "type": "bar"
        }],
        "layout": {
            "title": "Commodity Quantity (Last 5 Minutes)",
            "xaxis": {"title": "Commodity"},
            "yaxis": {"title": "Net Quantity"}
        }
    }


@app.callback(
    dash.dependencies.Output("summary", "children"),
    [dash.dependencies.Input("interval", "n_intervals")]
)
def update_summary(n):
    conn = psycopg2.connect(
        host="postgres",
        database="transactions_db",
        user="user",
        password="password"
    )
    transactions = pd.read_sql_query("SELECT commodity, quantity FROM transactions", conn)
    prices = pd.read_sql_query("SELECT commodity, price FROM prices", conn)
    conn.close()

    if transactions.empty:
        return html.Div("No transaction data available")

    quantity_by_commodity = transactions.groupby("commodity", as_index=False)["quantity"].sum()
    latest_prices = prices.drop_duplicates(subset=["commodity"], keep="last") if not prices.empty else pd.DataFrame(columns=["commodity", "price"])
    summary = quantity_by_commodity.merge(latest_prices, on="commodity", how="left")
    summary["price"] = summary["price"].fillna(0)
    summary = summary.sort_values("commodity")

    rows = [[row.commodity, f"{row.quantity:.2f}", f"{row.price:.2f}"] for row in summary.itertuples(index=False)]
    return html.Div([
        html.H2("Commodity Summary"),
        build_table(["Commodity", "Quantity", "Price"], rows)
    ])

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)